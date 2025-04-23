#!/usr/bin/env python3
# vim: set fileencoding=utf-8:
"""
Enable GitHub Action workflows for specified repositories (ensures that they
are not disabled due to inactivity).
"""

# Standard library
import argparse
import sys
import traceback

# First-party/Local
import ccos.log
from ccos import gh_utils

LOG = ccos.log.setup_logger()


class ScriptError(Exception):
    def __init__(self, message, code=None):
        self.code = code if code else 1
        message = "({}) {}".format(self.code, message)
        super(ScriptError, self).__init__(message)


def setup():
    """
    Instantiate and configure argparse and logging.

    Return argsparse namespace.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "-n",
        "--dryrun",
        action="store_true",
        help="dry run: do not make any changes",
    )
    ap.add_argument(
        "repos",
        nargs="*",
        help="repository to act on (multiple repositories may be specified)",
        metavar="REPOSITORY",
    )
    args = ap.parse_args()
    if args.dryrun:
        args.dryrun = "dryrun (no-op): "
    else:
        args.dryrun = ""
    if not args.repos:
        raise ap.error("at least one (1) REPOSITORY must be specified")
    return args


def get_workflows(args, repos):
    workflows = []
    for repo in repos:
        for workflow in repo.get_workflows():
            workflow.repo_name = repo.name
            workflows.append(workflow)
    return workflows


def enable_workflows(args, workflows):
    for workflow in workflows:
        LOG.info(
            f"{args.dryrun}Enabling {workflow.repo_name}:"
            f' "{workflow.name}"'
        )
        if not args.dryrun:
            workflow.enable()


def main():
    args = setup()
    github_client = gh_utils.setup_github_rest_client()
    gh_org_cc = gh_utils.get_cc_organization(github_client)
    repos = gh_utils.get_select_repos(args, gh_org_cc)
    workflows = get_workflows(args, repos)
    enable_workflows(args, workflows)


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
