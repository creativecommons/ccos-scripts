#!/usr/bin/env python3

# Standard library
import logging
import os.path
import sys
import traceback

# First-party/Local
from ccos import log
from ccos.teams.get_community_team_data import get_community_team_data
from ccos.teams.set_codeowners import create_codeowners_for_data
from ccos.teams.set_teams_on_github import create_teams_for_data

log.set_up_logging()
logger = logging.getLogger(os.path.basename(__file__))
log.reset_handler()


class ScriptError(Exception):
    def __init__(self, message, code=None):
        self.code = code if code else 1
        message = "({}) {}".format(self.code, message)
        super(ScriptError, self).__init__(message)


def main():
    exit_status = 0
    exit_status = create_teams_for_data(get_community_team_data(), exit_status)
    create_codeowners_for_data(get_community_team_data())
    sys.exit(exit_status)


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
