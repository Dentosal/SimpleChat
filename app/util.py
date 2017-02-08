import re
import string
from os import urandom
from config import *
from hashlib import sha512

def try_float(candidate, default=None):
    m = re.match("\d+\.\d+$", candidate)
    if m:
        return float(m)
    else:
        return default

def parse_locale(locale):
    options = []
    if locale:
        if "," in locale:
            options += list(map(
                lambda lang: lang[0],
                sorted(
                    filter(
                        lambda lang: len(lang) in (1,2),
                        map(
                            lambda lang: [p.strip() for p in lang.split(";")],
                            locale.split(",")
                        )
                    ),
                    key=lambda lang: try_float(lang[1], 1.0) if len(lang)==2 else 1.0
                )
            ))
        m = re.match(r"[a-zA-Z]+", locale)
        if m:
            options.append(m.group(0))
    return options + [LOCALE_DEFAULT]

def gen_salt():
    return "".join(hex(byte)[2:] for byte in urandom(64))

def hash_password(password, salt):
    return sha512((password+salt).encode("utf-8")).hexdigest()

def check_username_chars(username):
    return all(c in string.ascii_letters+string.digits+"_" for c in username)

def check_credentials(username, password):
    return 3 < len(username) <= 100 and check_username_chars(username) and 8 < len(password) <= 100

def case_insensitive_match(search):
    return "".join(["["+c.lower()+c.upper()+"]" if c in string.ascii_letters else c for c in search])
