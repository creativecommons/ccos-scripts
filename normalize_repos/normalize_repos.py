#!/usr/bin/env python3
# vim: set fileencoding=utf-8:

"""
This script ensures that all active repositories in the creativecommons GitHub
organization are consistent. Please see README.md.
"""

# Standard library
import argparse
import logging
import sys
import traceback

#Third-party
from github import GithubException, UnknownObjectException
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


class ScriptError(Exception):
    def __init__(self, message, code=None):
        self.code = code if code else 1
        message = "({}) {}".format(self.code, message)
        super(ScriptError, self).__init__(message)


def setup():
    """Instantiate and configure argparse and logging.

    Return argsparse namespace.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "-r",
        "--repo",
        "--repository",
        action="append",
        help="select repository or repositories to update from those fetched"
        " from GitHub (may be specified multiple times)",
        metavar="REPO",
        dest="repos",
    )
    ap.add_argument(
        "--skip-branches", action="store_true", help="skip branches update",
    )
    ap.add_argument(
        "--skip-labels", action="store_true", help="skip labels update",
    )
    args = ap.parse_args()
    return args


def get_cc_repos(github):
    cc = get_cc_organization(github)
    return cc.get_repos()


def get_select_repos(args):
    # github = set_up_github_client()
    repos = list(get_cc_repos(github))
    if args.repos:
        repos_selected = []
        for repo in repos:
            if repo.name in args.repos:
                repos_selected.append(repo)
        repos = repos_selected
        if not repos:
            raise ScriptError(
                "Specified repositories do not include any valid"
                f" repositories: {args.repos}"
            )
    repos.sort(key=lambda repo: repo.name)
    return repos


def set_repo_labels(args, repos):
    if args.skip_labels:
        return
    logger.log(logging.INFO, "Syncing labels...")
    set_labels(repos, *get_labels())
    logger.log(log.SUCCESS, "done.")


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
    try:
        default_branch = repo.get_branch(repo.default_branch)
    except GithubException as e:
        if e.data["message"] == "Branch not found":
            logger.log(
                logging.WARNING,
                f"{repo.name}: skipping: default branch not found",
            )
            return
        else:
            raise
    if (
        repo.name not in branch_protections.EXEMPT_REPOSITORIES
        and is_engineering_project(repo)
    ):

        logger.log(logging.INFO, f"{repo.name}: updating branch protections")
        if repo.name in branch_protections.REQUIRED_STATUS_CHECK_MAP:
            default_branch.edit_protection(
                required_approving_review_count=1,
                user_push_restrictions=[],
                contexts=branch_protections.REQUIRED_STATUS_CHECK_MAP[
                    repo.name
                ],
            )
        else:
            default_branch.edit_protection(
                required_approving_review_count=1, user_push_restrictions=[]
            )
    else:
        logger.log(logging.INFO, f"{repo.name}: skipping: exempt")


def update_branches(args, repos):
    if args.skip_branches:
        return
    logger.log(
        logging.INFO, "Evaluting repositories for branch protections...",
    )
    for repo in repos:
        # TODO: Set up automatic deletion of merged branches
        update_branch_protection(repo)
    logger.log(log.SUCCESS, "done.")


def main():
    args = setup()
    logger.log(logging.INFO, "Starting normalization")
    repos = get_select_repos(args)
    set_repo_labels(args, repos)
    update_branches(args, repos)


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
    except KeyboardInterrupt:
        logger.log(logging.INFO, "Halted via KeyboardInterrupt.")
        sys.exit(130)
    except ScriptError:
        error_type, error_value, error_traceback = sys.exc_info()
        logger.log(logging.CRITICAL, f"{error_value}")
        sys.exit(error_value.code)
    except Exception:
        logger.log(
            logging.ERROR, f"Unhandled exception: {traceback.format_exc()}"
        )
        sys.exit(1)
