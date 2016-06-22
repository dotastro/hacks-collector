import os
import re
import time

import requests
from flask import Flask, request
from github import Github

GITHUB_API_URL = 'https://api.github.com/'

app = Flask(__name__)

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

BLOCK_PATTERN = re.compile('\[#.+\]', flags=re.DOTALL)
ISSUE_PATTERN = re.compile('#[0-9]+')


def find_prs_in_changelog(content):
    issue_numbers = []
    for block in BLOCK_PATTERN.finditer(content):
        block_start, block_end = block.start(), block.end()
        block = content[block_start:block_end]
        for m in ISSUE_PATTERN.finditer(block):
            start, end = m.start(), m.end()
            issue_numbers.append(int(block[start:end][1:]))
    return issue_numbers

def find_prs_in_changelog_by_section(content):

    changelog_prs = {}
    version = None
    subcontent = ''
    previous = None

    for line in content.splitlines():
        if '-------' in line:
            if version is not None:
                for pr in find_prs_in_changelog(subcontent):
                    changelog_prs[int(pr)] = version
            version = previous.strip().split('(')[0].strip()
            if not 'v' in version:
                version = 'v' + version
            subcontent = ''
        elif version is not None:
            subcontent += line
        previous = line

    return changelog_prs


@app.route("/hook", methods=['POST'])
def hook():

    # We need to make sure we don't reply too quickly, to make sure the comment
    # ends up below the merge message.
    time.sleep(2)

    # Only check pull requests
    if request.headers['X-GitHub-Event'] != 'pull_request':
        return 'No action needed'

    # Only consider merge events
    if request.json['action'] != 'closed' or request.json['pull_request']['merged_at'] is None:
        return 'No action needed'

    merged_by = request.json['pull_request']['merged_by']['login']

    gh = Github(login_or_token=GITHUB_TOKEN)
    repo = gh.get_repo(request.json['pull_request']['base']['repo']['full_name'])
    pr = repo.get_pull(int(request.json['number']))

    issues = []

    milestone = request.json['pull_request']['milestone']

    if milestone is None:
        issues.append("The milestone has not been set")

    issue = repo.get_issue(pr.number)
    labels = [label.name for label in issue.labels]

    changelog_entry = False
    for fl in pr.get_files():
        if fl.filename == 'CHANGES.rst':
            changelog = requests.get(requests.get(fl.contents_url).json()['download_url']).text
            sections = find_prs_in_changelog_by_section(changelog)
            changelog_entry = pr.number in sections
            if changelog_entry:
                if not milestone.startswith(sections[pr.number]):
                    issues.append("Changelog entry section ({0}) inconsistent with milestone ({1})".format(sections[pr.number], milestone))

    if 'no-changelog-entry-needed' in labels:
        if changelog_entry:
            issues.append("Changelog entry present but **no-changelog-entry-needed** label set")
    elif 'Affects-dev' in labels:
        if changelog_entry:
            issues.append("Changelog entry present but **Affects-dev** label set")
    else:
        if not changelog_entry:
            issues.append("Changelog entry not present (or pull request number missing) and neither the **Affects-dev** nor the **no-changelog-entry-needed** label are set")

    if len(issues) > 0:

        message = "@{0} - thanks for merging this! However, I noticed the following issues with this pull request:\n\n".format(merged_by)
        for issue in issues:
            message += "* {0}\n".format(issue)

        message += "\nWould it be possible to fix these? Thanks! \n"

        if len(issues) == 1:
            message = message.replace('issues with', 'issue with').replace('fix these', 'fix this')

        message += "\n*This is an experimental bot being written by @astrofrog - let me know if the message above is incorrect!*\n"

        pr.create_issue_comment(message)

        return message

    else:

        return "All good!"

if __name__ == "__main__":
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port)
    app.run(debug=True)
