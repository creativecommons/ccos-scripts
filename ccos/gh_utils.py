# Standard library
import inspect
import logging
import os
import sys

# Third-party
from github import Github
from github.GithubException import BadCredentialsException

# First-party/Local
from ccos import log

log_name = os.path.basename(os.path.splitext(inspect.stack()[-1].filename)[0])
logger = logging.getLogger(log_name)
log.reset_handler()

GITHUB_ORGANIZATION = "creativecommons"
GITHUB_USERNAME = "cc-creativecommons-github-io-bot"
GITHUB_TOKEN = None


def set_up_github_client():
    global GITHUB_TOKEN
    try:
        GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]
    except KeyError:
        logger.critical("missin ADMIN_GITHUB_TOKEN environment variable")
        sys.exit(1)
    logger.log(logging.INFO, "Setting up GitHub client...")
    github_client = Github(GITHUB_TOKEN)
    logger.log(log.SUCCESS, "done.")
    return github_client


def get_cc_organization(github_client):
    logger.log(logging.INFO, "Getting CC's GitHub organization...")
    try:
        cc = github_client.get_organization(GITHUB_ORGANIZATION)
    except BadCredentialsException as e:
        logger.critical(
            f"{e.status} {e.data['message']} (see"
            f" {e.data['documentation_url']})"
        )
        sys.exit(1)
    logger.log(log.SUCCESS, "done.")
    return cc
