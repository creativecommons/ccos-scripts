#!/usr/bin/env python3
# vim: set fileencoding=utf-8:

"""
This script ensures that all active repositories in the creativecommons GitHub
organization are consistent. Please see README.md.
"""

# Standard library
import logging

# Third-party
from github import UnknownObjectException
import yaml  # For converting .cc-metadata.yml to Python dictionary

# Local/library specific
from get_labels import get_labels
from set_labels import set_labels
from utils import get_cc_organization, set_up_github_client
import branch_protections
import log


log.set_up_logging()
logger = logging.getLogger("normalize_repos")
log.reset_handler()


def get_cc_repos(github):
    cc = get_cc_organization(github)
    return cc.get_repos()


def is_engineering_project(repo):
    try:
        contents = repo.get_contents(".cc-metadata.yml")
    except UnknownObjectException:
        # Implies that there is no .cc-metadata.yml file in the repository
        return False
    contents = contents.decoded_content
    metadata = yaml.safe_load(contents)
    return metadata.get("engineering_project", False)


def update_branch_protection(repo):
    master = repo.get_branch("master")
    if (
        repo.name not in branch_protections.EXEMPT_REPOSITORIES
        and is_engineering_project(repo)
    ):
        if repo.name in branch_protections.REQUIRED_STATUS_CHECK_MAP:
            master.edit_protection(
                required_approving_review_count=1,
                user_push_restrictions=[],
                contexts=branch_protections.REQUIRED_STATUS_CHECK_MAP[
                    repo.name
                ],
            )
        else:
            master.edit_protection(
                required_approving_review_count=1, user_push_restrictions=[]
            )
        print(f'Updating branch protection for: "{repo.name}"')
    else:
        print(f'Skipping branch protection for exempt repo: "{repo.name}"')


if __name__ == "__main__":
    logger.log(logging.INFO, "Starting normalization")
    logger.log(logging.INFO, "Syncing labels...")
    set_labels(*get_labels())
    logger.log(log.SUCCESS, "done.")

    github = set_up_github_client()
    repos = get_cc_repos(github)

    for repo in repos:
        # TODO: Set up automatic deletion of merged branches
        update_branch_protection(repo)
