import os
import uuid
import requests
from urllib.parse import urlencode, parse_qs

from flask import Flask, request, send_from_directory, redirect
from github import Github

GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'

HACKLIST_REPO = 'dotastro/hack-list'

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory('form', 'form-validation.html')

@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory('form/assets', filename)


@app.route("/create", methods=['POST'])
def github_authorize():
    data = {'client_id': CLIENT_ID,
            'redirect_uri': request.base_url + '?' + urlencode(request.form)}
    pr = requests.Request('GET', GITHUB_AUTH_URL, params=data).prepare()
    return redirect(pr.url)

@app.route("/create", methods=['GET'])
def create_post():
    data = {'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': request.args['code']}
    res = requests.post(GITHUB_TOKEN_URL, data=data)
    token = parse_qs(res.text)['access_token'][0]
    return token
    gh = Github(token)
    return str(request.args)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
