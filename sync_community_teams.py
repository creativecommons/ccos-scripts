#!/usr/bin/env python3

"""
Create GitHub teams for the Community teams and update their membership based
on the community_team_members.json Lektor databag.
"""

# Standard library
import argparse
import logging
import sys
import traceback

# First-party/Local
import ccos.log
from ccos.teams.get_community_team_data import get_community_team_data
from ccos.teams.set_codeowners import create_codeowners_for_data
from ccos.teams.set_teams_on_github import create_teams_for_data

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
        "-d",
        "--debug",
        action="store_true",
        help="Debug mode: show differences instead of making changes",
    )
    args = ap.parse_args()
    return args


def main():
    args = setup()
    if args.debug:
        LOG.setLevel(logging.DEBUG)
        LOG.debug("Debug mode: no changes will be made to GitHub repositories")
    else:
        LOG.info("Synchronizing community teams")
    community_team_data = get_community_team_data()
    if not args.debug:
        create_teams_for_data(community_team_data)
    else:
        LOG.debug("skipping team updates")
    create_codeowners_for_data(args, community_team_data)


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
