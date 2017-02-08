import redis
import json
import time
import random

import config
from util import *

class Database(object):
    """
        A database conncetion manager and action wrapper.

        Databases:

        db | Purpose
        ---|--------
        0  | Usernames, password hashes and salts
        1  | Channel names and joined users
        2  | Messages in channels
        3  | Private messages

        db | Format
        ---|--------
        0  | Map(username    -> pw_hash:pw_salt)
        1  | Map(channelname -> Set(user_name))
        2  | Map(channelname -> List(message_info)) and Map(channelname:"modified" -> timestamp)
        3  | Map(user1:user2 -> List(message_info)) and Map(user1:user2:"modified" -> timestamp)
    """
    def __init__(self):
        self.db_users     = redis.StrictRedis(db=0) # Map(username    -> pw_hash:pw_salt)
        self.db_channels  = redis.StrictRedis(db=1) # Map(channelname -> Set(user_name))
        self.db_c_msgs    = redis.StrictRedis(db=2) # Map(channelname -> List(message_info)) and Map(channelname:"modified" -> timestamp)
        self.db_p_msgs    = redis.StrictRedis(db=3) # Map(user1:user2 -> List(message_info)) and Map(user1:user2:"modified" -> timestamp)

        try:
            self.db_users.ping()
        except redis.exceptions.ConnectionError:
            exit("Could not connect to Redis database.")

    @staticmethod
    def userpair(user1, user2):
        return ":".join(sorted((user1, user2)))

    def user_exists(self, name):
        return self.db_users.exists(name)

    def channel_exists(self, name):
        return self.db_channels.exists(name)

    def user_login(self, username, password):
        # sanitize input
        if not check_username_chars(username):
            return False
        # get login data
        login_data = self.db_users.get(username)
        if login_data is None:
            # user does not exist
            return False
        else:
            # randomize delay to prevent time-based side channel attacks
            time.sleep(config.LOGIN_DELAY*(1+random.random()*LOGIN_DELAY))
            # test if the password is correct
            pw_hash, pw_salt = login_data.decode("utf-8").split(":", 1)
            return pw_hash == hash_password(password, pw_salt)

    def user_create(self, username, password):
        assert ":" not in username, "Unreachable! Username contains a colon."

        salt = gen_salt()
        value = hash_password(password, salt)+":"+salt
        return self.db_users.setnx(username, value)

    def get_messages(self, user1, user2):
        msgs = self.db_p_msgs.lrange(Database.userpair(user1, user2), 0, -1)
        if msgs is None:
            return None
        else:
            return [json.loads(msg.decode("utf-8")) for msg in msgs]

    def get_messages_channel(self, channel):
        msgs = self.db_c_msgs.lrange(channel, 0, -1)
        if msgs is None:
            return None
        else:
            return [json.loads(msg.decode("utf-8")) for msg in msgs]

    def join_channel(self, user, channel):
        self.db_channels.sadd(channel, user)

    def get_chats(self, username):
        chats = []
        # this pattern with username is guranteed matcb all instances, but it may also give false positives
        for chat in self.db_p_msgs.scan_iter(match="*"+username+"*"):
            participants = chat.decode("utf-8").split(":")

            if len(participants) == 2: # skip modifications times here
                if username in participants:
                    # select other user
                    other = participants[1-participants.index(username)]
                    # get modification time
                    modified = int(self.db_p_msgs.get(":".join(participants+["modified"])).decode("utf-8"))
                    chats.append((
                        modified,
                        {"name": other, "isChannel": False, "lastModified": modified}
                    ))

        for channel in self.db_channels.scan_iter():
            channel = channel.decode("utf-8")
            if self.db_channels.sismember(channel, username):
                # get modification time
                modified_raw = self.db_c_msgs.get(channel+":modified")
                if modified_raw is None:
                    modified = 0
                else:
                    modified = int(modified_raw.decode("utf-8"))
                chats.append((
                    modified,
                    {"name": channel, "isChannel": True, "lastModified": modified}
                ))

        return [data for modified, data in sorted(chats, reverse=True)] # newest is first

    def send_message(self, db, key, msg, from_user, to):
        timestamp = int(time.time()*1000)

        # concatenate multiple consecutive messages, if they are send less than minute from each other
        append_normally = True
        latest_data = db.lindex(key, 0)
        if latest_data is not None:
            latest = json.loads(latest_data.decode("utf-8"))
            if latest["from"] == from_user and latest["time"] > timestamp - 1000*60:
                # concatenate
                latest["message"] += "\n" + msg
                db.lset(key, 0, json.dumps(latest).encode("utf-8"))
                append_normally = False

        if append_normally:
            db.lpush(
                key,
                json.dumps({
                    "message": msg,
                    "time": timestamp,
                    "from": from_user,
                    "to": to
                }).encode("utf-8")
            )

        db.set(key+":modified", timestamp)
        return True

    def send_message_to_user(self, msg, from_user, to_user):
        user_exists = self.user_exists(to_user)
        if user_exists:
            self.send_message(self.db_p_msgs, Database.userpair(from_user, to_user), msg, from_user, to_user)
        return user_exists

    def send_message_to_channel(self, msg, from_user, to_channel):
        in_channel = self.db_channels.sismember(to_channel, from_user)
        if in_channel:
            self.send_message(self.db_c_msgs, to_channel, msg, from_user, to_channel)
        return in_channel

    def search(self, search):
        search = search.strip()
        if search:
            matches = []

            channels_only = False
            if search.startswith("!"):
                channels_only = True
                search = search[1:]
                if not search:
                    return []

            # if invalid characters
            if not check_username_chars(search):
                return []

            # case insensitive search
            matchstring = case_insensitive_match(search)

            if self.channel_exists(search):
                matches.append("#"+search)

            if not channels_only:
                if self.user_exists(search):
                    matches.append(search)
                users = list(name.decode("utf-8") for name in self.db_users.scan_iter(match=matchstring+"*", count=5))
                matches += [user for user in users if user not in matches] # dedup

            channels = list("#"+name.decode("utf-8") for name in self.db_channels.scan_iter(match=matchstring+"*", count=5))
            channels = [channel for channel in channels if channel not in matches] # dedup
            matches = matches[:3+max(0, 2-len(channels))] + channels # limit number of channels

            return matches[:5] # five first matches
        else:
            return []
