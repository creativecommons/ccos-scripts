from github import Github
import os

GITHUB_ORGANIZATION = "creativecommons"
GITHUB_USERNAME = "cc-creativecommons-github-io-bot"
GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]


def set_up_github_client():
    print("Setting up GitHub client...")
    github_client = Github(GITHUB_TOKEN)
    return github_client


def get_cc_organization(github_client):
    print("Getting CC's GitHub organization...")
    cc = github_client.get_organization(GITHUB_ORGANIZATION)
    return cc