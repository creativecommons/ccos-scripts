#!/usr/bin/env python3
# vim: set fileencoding=utf-8:

# Standard library
import argparse
import logging
import os.path
import sys
import traceback

# First-party/Local
from ccos import log
from ccos.data.get_community_team_data import (
    get_community_team_data,
    setup_asana_client,
)
from ccos.data.get_repo_data import get_repo_data, get_repo_names
from ccos.data.push_data_via_git import push_data

DAILY_DATABAGS = ["repos", "community_team_members"]

log.set_up_logging()
logger = logging.getLogger(os.path.basename(__file__))
log.reset_handler()


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
    asana_client = setup_asana_client()
    if "repos" in args.databags:
        logger.log(logging.INFO, "updating repos.json")
        push_data(get_repo_data(), "repos.json")
    if "community_team_members" in args.databags:
        logger.log(logging.INFO, "community_team_members.json")
        repo_names = get_repo_names()
        community_data = get_community_team_data(asana_client, repo_names)
        push_data(community_data, "community_team_members.json")


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
