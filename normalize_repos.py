#!/usr/bin/env python3

"""
This script ensures that all active repositories in the creativecommons GitHub
organization are consistent. Please see README.md.
"""

# Standard library
import argparse
import sys
import traceback

# Third-party
import yaml  # For converting .cc-metadata.yml to Python dictionary
from github import GithubException, UnknownObjectException

# First-party/Local
import ccos.log
from ccos import gh_utils
from ccos.norm.get_labels import get_labels, get_required_label_groups
from ccos.norm.set_labels import set_labels
from ccos.norm.validate_issues import validate_issues

LOG = ccos.log.setup_logger()


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
        "--skip-branches",
        action="store_true",
        help="skip branches update",
    )
    ap.add_argument(
        "--skip-labels",
        action="store_true",
        help="skip labels update",
    )
    ap.add_argument(
        "--skip-issues", action="store_true", help="skip issue labels check"
    )
    args = ap.parse_args()
    return args


def set_repo_labels(args, repos):
    if args.skip_labels:
        return
    LOG.info("Syncing labels...")
    set_labels(repos, *get_labels())
    LOG.success("done.")


def validate_issue_labels(args, repos):
    if args.skip_issues:
        return
    LOG.info("Checking issues...")
    required_label_groups = get_required_label_groups()
    validate_issues(repos, required_label_groups)
    LOG.success("done.")


def is_engineering_project(repo):
    try:
        contents = repo.get_contents(".cc-metadata.yml")
    except UnknownObjectException:
        # Implies that there is no .cc-metadata.yml file in the repository
        return False
    contents = contents.decoded_content
    metadata = yaml.safe_load(contents)
    return metadata.get("engineering_project", False)


def load_branch_protection_config():
    with open("branch_protections.yml", "r") as file:
        config = yaml.safe_load(file)
    return config


def update_branch_protection(repo):
    try:
        default_branch = repo.get_branch(repo.default_branch)
    except GithubException as e:
        if e.data["message"] == "Branch not found":
            LOG.warning(f"{repo.name}: skipping: default branch not found")
            return
        else:
            raise
    config = load_branch_protection_config()
    exempt_repositories = config["EXEMPT_REPOSITORIES"]
    required_status_check_map = config["REQUIRED_STATUS_CHECK_MAP"]
    if repo.name not in exempt_repositories and is_engineering_project(repo):
        LOG.info(f"{repo.name}: updating branch protections")
        # The following empty *_bypass_pull_request_allowance arguments ensure
        # the required bypass_pull_request_allowances API parameter is
        # populated:
        # https://docs.github.com/rest/branches/branch-protection#update-branch-protection
        if repo.name in required_status_check_map:
            default_branch.edit_protection(
                required_approving_review_count=1,
                user_push_restrictions=[],
                contexts=required_status_check_map[repo.name],
                users_bypass_pull_request_allowances=[],
                teams_bypass_pull_request_allowances=[],
                apps_bypass_pull_request_allowances=[],
            )
        else:
            default_branch.edit_protection(
                required_approving_review_count=1,
                user_push_restrictions=[],
                users_bypass_pull_request_allowances=[],
                teams_bypass_pull_request_allowances=[],
                apps_bypass_pull_request_allowances=[],
            )
    else:
        LOG.info(f"{repo.name}: skipping: exempt")


def update_branches(args, repos):
    if args.skip_branches:
        return
    LOG.info("Evaluting repositories for branch protections...")
    for repo in repos:
        update_branch_protection(repo)
    LOG.success("done.")


def main():
    args = setup()
    LOG.info("Starting normalization")
    repos = gh_utils.get_select_repos(args)
    set_repo_labels(args, repos)
    validate_issue_labels(args, repos)
    update_branches(args, repos)


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
    except KeyboardInterrupt:
        LOG.info("Halted via KeyboardInterrupt.")
        sys.exit(130)
    except ScriptError:
        error_type, error_value, error_traceback = sys.exc_info()
        LOG.critical(f"{error_value}")
        sys.exit(error_value.code)
    except Exception:
        LOG.error(f"Unhandled exception: {traceback.format_exc()}")
        sys.exit(1)
