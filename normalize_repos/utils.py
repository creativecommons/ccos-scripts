# Standard library
import os
import logging

# Third party
from github import Github

# Local/library specific
import log


logger = logging.getLogger("normalize_repos")
log.reset_handler()

GITHUB_ORGANIZATION = "creativecommons"
GITHUB_USERNAME = "cc-creativecommons-github-io-bot"
GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]

COLORS = {
    "UNFAVOURABLE": "b60205",
    "NEGATIVE": "ff9f1c",
    "NEUTRAL": "ffcc00",
    "POSITIVE": "cfda2c",
    "FAVOURABLE": "008672",
    "BLACK": "000000",
    "DARKER": "333333",
    "DARK": "666666",
    "MEDIUM": "999999",
    "LIGHT": "cccccc",
    "LIGHTER": "eeeeee",
    "WHITE": "ffffff",
}


def set_up_github_client():
    logger.log(logging.INFO, "Setting up GitHub client...")
    github_client = Github(GITHUB_TOKEN)
    logger.log(log.SUCCESS, "done.")
    return github_client


def get_cc_organization(github_client):
    logger.log(logging.INFO, "Getting CC's GitHub organization...")
    cc = github_client.get_organization(GITHUB_ORGANIZATION)
    logger.log(log.SUCCESS, "done.")
    return cc
