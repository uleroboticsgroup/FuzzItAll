from flask import Flask, request, jsonify
import subprocess
app = Flask(__name__)

allowed_users = ['eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkRBdmlkIiwiaWF0IjoxNTE2MjM5MDIyfQ.PRwp0fk9estoeVaO3FisJpERB5hivewMt8B7L2hY8Wk']

FUZZER_DIRECTORY='/data/th3fuzz3r/'
FUZZER_PATH="/data/th3fuzz3r/fuzzitall.sh"
STATUS_PATH='/data/th3fuzz3r/status.sh'

def auth(token):
    if token and token in allowed_users:
        return True
    
    return False

@app.route('/api/new_job', methods=['POST'])
def new_job():
    content = request.json
    if not auth(content['token']):
        return 'Not allowed'
        
    project_name = content['project']
    git = content['git_ssh_endpoint']

    subprocess.run(['./new-job.sh', project_name, git])
    return "OK " + project_name + " " + git

@app.route('/api/status', methods=['POST'])
def status():
    content = request.json
    if not auth(content['token']):
        return 'Not allowed'
    
    project_name = content['project']
    git = content['git-project-name']

    process = subprocess.run(['./status.sh', project_name, git], stdout=subprocess.PIPE)
    return process.stdout

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)