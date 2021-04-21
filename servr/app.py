from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp, generate_password_hash, check_password_hash
import sqlite3
import subprocess
app = Flask(__name__)


app.config["DATABASE"] = './database.db'
app.config['SECRET_KEY'] = 'ea52503b822061bb0cba460xaaaq946e8e9f5d2d55db38b6657fc7d371a0e8ce396cb'

FUZZER_DIRECTORY='/data/fuzzitall/'
FUZZER_PATH= FUZZER_DIRECTORY + "fuzzitall.sh"
STATUS_PATH= FUZZER_DIRECTORY + 'status.sh'


@app.route('/api/new_job', methods=['POST'])
@jwt_required()
def new_job():
    content = request.json
    if not auth(content['token']):
        return 'Not allowed'
        
    project_name = content['project']
    git = content['git_ssh_endpoint']

    subprocess.run(['./new-job.sh', project_name, git])
    return "OK " + project_name + " " + git

@app.route('/api/status', methods=['POST'])
@jwt_required()
def status():
    content = request.json
    if not auth(content['token']):
        return 'Not allowed'
    
    project_name = content['project']
    git = content['git-project-name']

    process = subprocess.run(['./status.sh', project_name, git], stdout=subprocess.PIPE)
    return process.stdout


@app.route('/register', methods=['POST'])
@jwt_required()
def register():
    content = request.json

    if not 'username' in content.keys():
        error = 'Username is required.'
        return error
    elif not 'password' in content.keys():
        error = 'Password is required.'
        return error

    username = content['username']
    password = content['password']
    db = get_db()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif db.execute(
        'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone() is not None:
        error = 'User {} is already registered.'.format(username)

    if error is None:
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()
        return 'OK'

    return error

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


from db import *
from auth import *
init_app(app)
jwt = JWT(app, authenticate, identity)

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True, port=9999)