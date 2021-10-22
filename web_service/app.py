from flask import Flask, request, jsonify, render_template, send_file
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp, generate_password_hash, check_password_hash
import sqlite3
import subprocess
app = Flask(__name__)

#admin:veryVerySecurePassword2021

app.config["DATABASE"] = './database.db'
app.config['SECRET_KEY'] = 'ea52503b822061bb0cba460xaaaq946e8e9f5d2d55db38b6657fc7d371a0e8ce396cb'

FUZZER_DIRECTORY='/data/fuzzitall/'
FUZZER_PATH= FUZZER_DIRECTORY + "fuzzitall.sh"
STATUS_PATH= FUZZER_DIRECTORY + 'status.sh'

def get_jobs(current_user):
    db = get_db()
    result = ''

    jobs = db.execute(
        'SELECT * FROM jobs WHERE author_id = ?', (current_user.id,)
    ).fetchall()

    for job in jobs:
        result += f'({job["id"]}) {job["project"]} --- Created at: {job["created"]}. \n'

    return result

@app.route('/api/results', methods=['GET'])
@jwt_required()
def results():
    project_id = request.args.get("id")
    db = get_db()

    job = db.execute(
        'SELECT * FROM jobs WHERE id = ? and author_id = ?', (project_id, current_identity.id,)
    ).fetchone()

    if job is None:
        return 'There is no job with that ID or your are not authorized to see it.'

    process = subprocess.run(['./get_results.sh', job['project'], job['sshProject']], stdout=subprocess.PIPE)
    return send_file(f"outputs/{job['project']}/{job['project']}.tar.gz", as_attachment=True)


@app.route('/api/new_job', methods=['POST'])
@jwt_required()
def new_job():
    content = request.json
    project_name = content['project']
    git = content['git-ssh-endpoint']
    db = get_db()

    if db.execute(
        'SELECT * FROM jobs WHERE project = ?', (project_name,)
    ).fetchone() is not None:
        return 'A job with that name already exists'

    db.execute(
        'INSERT INTO jobs (status, author_id, project, sshProject) VALUES (?, ?, ?, ?)',
        (False, current_identity.id, project_name, git[git.rfind('/')+1: git.rfind('.')])
    )
    db.commit()
    subprocess.run(['./new-job.sh', project_name, git])
    return get_jobs(current_identity)

@app.route('/api/status', methods=['GET'])
@jwt_required()
def status():
    project_id = request.args.get("id")
    if project_id is not None:
        db = get_db()

        job = db.execute(
            'SELECT * FROM jobs WHERE id = ? and author_id = ?', (project_id, current_identity.id,)
        ).fetchone()

        if job is None:
            return 'There is no job with that ID or your are not authorized to see it.'

        process = subprocess.run(['./status.sh', job['project'], job['sshProject']], stdout=subprocess.PIPE)
        return process.stdout
    else:
        return get_jobs(current_identity)


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


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html') 

from db import *
from auth import *
init_app(app)
jwt = JWT(app, authenticate, identity)

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True, port=9999)