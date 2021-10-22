from flask import Flask, request, jsonify, current_app, g
from flask.cli import with_appcontext

from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp, generate_password_hash, check_password_hash
import sqlite3

from db import *

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

def create_object(row):
    return User(row['id'], row['username'], row['password'])

def authenticate(username, password):
    content = request.json
    db = get_db()
    error = None
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'
        return None
    else:
        user = create_object(user)

    return user

def identity(payload):
    user_id = payload['identity']
    db = get_db()
    error = None
    print(user_id)
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()

    if user is None:
        error = 'Incorrect username.'
        return None

    user = create_object(user)
    return user