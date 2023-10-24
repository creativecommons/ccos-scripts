#!/usr/bin/env python3
"""
Ensure all open issues are tracked in the Backlog project in the Pending Review
column and all open pull requests are tracked in the Active Sprint project in
the Code Review column.
"""

# Standard library
import argparse
import sys
import traceback

# First-party/Local
import ccos.log
from ccos import gh_utils

ISSUES_COLUMN = "Pending Review"
ISSUES_PROJECT = "Backlog"
LOG = ccos.log.setup_logger()
PULL_REQUESTS_COLUMN = "Code Review"
PULL_REQUESTS_PROJECT = "Active Sprint"


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
        "-n",
        "--dryrun",
        action="store_true",
        help="dry run: do not make any changes",
    )
    args = ap.parse_args()
    return args


def get_untracked_issues(github_client):
    LOG.info("Searching for untracked open issues")
    # https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests
    query = (
        "org:creativecommons state:open -project:creativecommons/7"
        " -project:creativecommons/10 type:issue"
    )
    LOG.debug(f"issues query: {query}")
    untracked_issues = list(github_client.search_issues(query=query))
    untracked_issues.sort(key=lambda x: f"{x.repository.name}{x.number:09}")
    return untracked_issues


def track_issues(args, gh_org_cc, untracked_issues):
    if not untracked_issues:
        LOG.info(
            f"No untracked issues to add to {ISSUES_PROJECT}: {ISSUES_COLUMN}"
        )
        return
    LOG.info(
        f"Adding {len(untracked_issues)} issues to {ISSUES_PROJECT}:"
        f" {ISSUES_COLUMN}"
    )
    for project in gh_org_cc.get_projects():
        if project.name != ISSUES_PROJECT:
            continue
        for column in project.get_columns():
            if column.name != ISSUES_COLUMN:
                continue
            for issue in untracked_issues:
                if not args.dryrun:
                    no_op = ""
                    column.create_card(
                        content_id=issue.id,
                        content_type="Issue",
                    )
                else:
                    no_op = "(no-op) "
                LOG.change_indent(+1)
                LOG.success(
                    f"{no_op}{issue.repository.name}#{issue.number}"
                    f" {issue.title}"
                )
                LOG.change_indent(-1)


def get_untracked_pull_requests(github_client):
    LOG.info("Searching for untracked open pull requests")
    # https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests
    query = (
        "org:creativecommons state:open -project:creativecommons/7"
        " -project:creativecommons/10 type:pr"
    )
    LOG.debug(f"pull request query: {query}")
    untracked_pull_requests = list(github_client.search_issues(query=query))
    untracked_pull_requests.sort(
        key=lambda x: f"{x.repository.name}{x.number:09}"
    )
    return untracked_pull_requests


def track_pull_requests(args, gh_org_cc, untracked_pull_requests):
    if not untracked_pull_requests:
        LOG.info(
            f"No untracked pull requests to add to {PULL_REQUESTS_PROJECT}:"
            f" {PULL_REQUESTS_COLUMN}"
        )
        return
    LOG.info(
        f"Adding {len(untracked_pull_requests)} pull requests to"
        f" {PULL_REQUESTS_PROJECT}: {PULL_REQUESTS_COLUMN}"
    )
    for project in gh_org_cc.get_projects():
        if project.name != PULL_REQUESTS_PROJECT:
            continue
        for column in project.get_columns():
            if column.name != PULL_REQUESTS_COLUMN:
                continue
            for pull_request in untracked_pull_requests:
                if not args.dryrun:
                    no_op = ""
                    column.create_card(
                        content_id=pull_request.id,
                        # Based on the code samples I found elsewhere, I
                        # expect this to be "PullRequest", but that doesn't
                        # work and "Issue" does ¯\_(ツ)_/¯
                        content_type="Issue",
                    )
                else:
                    no_op = "(no-op) "
                LOG.change_indent(+1)
                LOG.success(
                    f"{no_op}{pull_request.repository.name}"
                    f"#{pull_request.number} {pull_request.title}"
                )
                LOG.change_indent(-1)


def main():
    args = setup()
    github_client = gh_utils.set_up_github_client()
    gh_org_cc = gh_utils.get_cc_organization(github_client)
    untracked_issues = get_untracked_issues(github_client)
    track_issues(args, gh_org_cc, untracked_issues)
    untracked_pull_requests = get_untracked_pull_requests(github_client)
    track_pull_requests(args, gh_org_cc, untracked_pull_requests)


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
