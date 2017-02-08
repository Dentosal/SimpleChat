#!/usr/bin/env python3

import sys
if not (sys.version_info[0] == 3 and sys.version_info[1] >= 5):
    print("Python 3.5 or newer required.")
    sys.exit(1)

from flask import Flask, session, request, redirect, url_for, abort
from flask import render_template, send_from_directory, jsonify
from functools import wraps

import util
from db import *

def page_required_auth(f):
    """Full page, requires user to be logged in to access, otherwise redirects to login."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" in session:
            return f(*args, **kwargs)
        else:
            return redirect("/login")
    return wrapper

def page_required_no_auth(f):
    """Full page, requires user to be logged out to access, otherwise redirects to main page."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" in session:
            return redirect("/")
        else:
            return f(*args, **kwargs)
    return wrapper

def api_required_auth(f):
    """API endpoint, requires user to be logged in to access, otherwise gives error 403."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" in session:
            return f(*args, **kwargs)
        else:
            abort(403) # forbidden
    return wrapper

def api_required_no_auth(f):
    """API endpoint, requires user to be logged out to access, otherwise gives error 400."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" in session:
            abort(400) # bad request
        else:
            return f(*args, **kwargs)
    return wrapper

app = Flask(__name__)
app.secret_key = "".join(util.hash_password(util.gen_salt(), util.gen_salt()))  # sha512-hash of 128 bits from os.urandom

db = Database()


@app.route("/favicon.ico")
def favicon():
    """Favicon."""
    return send_from_directory("static/", "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/")
@page_required_auth
def index():
    """Main chat view."""
    return render_template("home.html", username=session["username"])

@app.route("/login")
@page_required_no_auth
def login():
    """Login page."""
    return render_template("login.html")

@app.route("/register")
@page_required_no_auth
def register():
    """Register page."""
    return render_template("register.html")

@app.route("/api/user/login", methods=["POST"])
@page_required_no_auth
def api_login():
    """API endpoint for login."""
    if "username" in request.form and "password" in request.form:
        un = request.form["username"]
        pw = request.form["password"]
        if check_credentials(un, pw):
            if db.user_login(request.form["username"], request.form["password"]):
                session["username"] = un
                return jsonify(success=True)
        return jsonify(success=False)
    abort(400) # invalid request

@app.route("/api/user/logout", methods=["POST"])
@page_required_auth
def logout():
    """API endpoint for logout."""
    session.pop("username", None)
    return jsonify(success=True)

@app.route("/api/user/locale")
def api_user_locale():
    """Returns a list of locale options from request headers, best first."""
    return jsonify(
        success=True,
        result=util.parse_locale(
            request.headers.get("Accept-Language")
        )
    )

@app.route("/api/user/exists/<username>")
def api_user_exists(username):
    """Tests if given user exists."""
    return jsonify(success=True, result=db.user_exists(username))

@app.route("/api/user/create", methods=["POST"])
def api_user_create():
    """Creates user account and logs in."""
    if "username" in request.form and "password" in request.form:
        un = request.form["username"]
        pw = request.form["password"]
        if check_credentials(un, pw):
            success = db.user_create(un, pw)
            if success:
                session["username"] = un
            return jsonify(success=success)
        else:
            return jsonify(success=False)

    abort(400) # invalid request

@app.route("/api/user/send/<username>", methods=["POST"])
@api_required_auth
def api_user_send(username):
    """Send message to given user."""
    if "message" in request.form:
        return jsonify(
            success=db.send_message_to_user(request.form["message"], session["username"], username)
        )
    abort(400)

@app.route("/api/user/chats")
@api_required_auth
def api_user_chats():
    """Lists all chats user is participating."""
    return jsonify(success=True, result=db.get_chats(session["username"]))

@app.route("/api/user/messages/<username>")
@api_required_auth
def api_user_messages(username):
    """Lists private messages between current and given user. Returns list of html strings."""
    msgs = db.get_messages(session["username"], username)
    if msgs is None:
        return jsonify(success=False)
    else:
        msgs = [render_template("message.html", **msg) for msg in msgs]
        return jsonify(success=True, result=msgs)

@app.route("/api/channel/join/<channel>", methods=["POST"])
@api_required_auth
def api_channel_join(channel):
    """Joins to given channel."""
    db.join_channel(session["username"], channel)
    return jsonify(success=True)

@app.route("/api/channel/send/<channel>", methods=["POST"])
@api_required_auth
def api_channel_send(channel):
    """Sends message to given channel. Requires that the user has already joined to the target channel."""
    if "message" in request.form:
        return jsonify(
            success=db.send_message_to_channel(request.form["message"], session["username"], channel)
        )
    abort(400)

@app.route("/api/channel/messages/<channel>")
@api_required_auth
def api_channel_messages(channel):
    """Lists messages on given channel. Returns list of html strings."""
    msgs = db.get_messages_channel(channel)
    if msgs is None:
        return jsonify(success=False)
    else:
        msgs = [render_template("message.html", **msg) for msg in msgs]
        return jsonify(success=True, result=msgs)

@app.route("/api/search/<search>")
@api_required_auth
def api_search(search):
    """Returns first matches for given search string. Prefix channels with "!"."""
    return jsonify(success=True, result=db.search(search))


if __name__ == "__main__":
    if config.SELFHOSTING_PUBLIC:
        print("Running...")
        print("WARNING: Not using HTTPS")
        app.run("0.0.0.0", port=config.SELFHOSTING_PORT)
    else:
        print("Running locally...")
        app.run()
