import os
import uuid
import requests

from flask import Flask, request, send_from_directory
from github import Github

GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

app = Flask(__name__)

def github_authorize():
    data = {'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'state': uuid.uuid4()}
    res = requests.get(GITHUB_AUTH_URL, data=data)

@app.route("/")
def index():
    return send_from_directory('form', 'form-validation.html')

@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory('form/assets', filename)

# @app.route("/form/<path:filename>")
# def getstatic(filename):
#     return send_from_directory('form', filename)

@app.route("/create", methods=['POST', 'GET'])
def create():
    token = github_authorize()

    if request.method == 'GET':
        print(request.args)
    elif request.method == 'POST':
        print(request.form)
    else:
        raise ValueError("I'm afraid I can't do that Dave")

    gh = Github(token)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port)
    app.run(debug=True, port=port)
