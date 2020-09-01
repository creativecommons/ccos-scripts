import os

# Third party
from github import Github


GITHUB_ORGANIZATION = "creativecommons"
GITHUB_USERNAME = "cc-creativecommons-github-io-bot"
GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]


COLORS = {
    'UNFAVOURABLE': 'b60205',
    'NEGATIVE': 'ff9f1c',
    'NEUTRAL': 'ffcc00',
    'POSITIVE': 'cfda2c',
    'FAVOURABLE': '008672',

    'DARKER': '333333',
    'DARK': '666666',
    'MEDIUM': '999999',
    'LIGHT': 'cccccc',
    'LIGHTER': 'eeeeee',

    'BLACK': '000000'
}


def set_up_github_client():
    print("Setting up GitHub client...")
    github_client = Github(GITHUB_TOKEN)
    return github_client


def get_cc_organization(github_client):
    print("Getting CC's GitHub organization...")
    cc = github_client.get_organization(GITHUB_ORGANIZATION)
    return cc
