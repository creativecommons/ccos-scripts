#!/usr/bin/env python3
# vim: set fileencoding=utf-8:

# Standard library
import argparse
import sys
import traceback

# First-party/Local
import ccos.log
from ccos import gh_utils
from ccos.data.asana import get_asana_team_members, setup_asana_client
from ccos.data.get_community_team_data import get_community_team_data
from ccos.data.get_repo_data import get_repo_data, get_repo_names
from ccos.data.push_data_via_git import push_data

DAILY_DATABAGS = ["repos", "community_team_members"]

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
    ap = argparse.ArgumentParser(description="Sync data to CCOS")
    ap.add_argument(
        "databags",
        action="store",
        nargs="*",
        default=DAILY_DATABAGS,
        help="the list of all databags to sync to CCOS",
    )
    args = ap.parse_args()
    return args


def main():
    args = setup()
    github_client = gh_utils.set_up_github_client()
    gh_org_cc = gh_utils.get_cc_organization(github_client)
    if "repos" in args.databags:
        LOG.info("updating repos.json")
        push_data(get_repo_data(gh_org_cc), "repos.json")
        LOG.success("done.")
    if "community_team_members" in args.databags:
        LOG.info("community_team_members.json")
        asana_client = setup_asana_client()
        team_members = get_asana_team_members(asana_client)
        repo_names = get_repo_names(gh_org_cc)
        community_data = get_community_team_data(team_members, repo_names)
        push_data(community_data, "community_team_members.json")
        LOG.success("done.")


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
