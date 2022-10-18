#!/usr/bin/env python3
"""
Move closed Issues out of Backlog and into Active Sprint: Done.
"""
# Standard library
import argparse
import logging
import os
import sys
import traceback

# First-party/Local
from ccos import gh_utils, log

log.set_up_logging()
logger = logging.getLogger(os.path.basename(__file__))
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
        "-n",
        "--dryrun",
        action="store_true",
        help="dry run: do not make any changes",
    )
    args = ap.parse_args()
    return args


def get_cards(cc):
    active = None
    backlog = None
    done = None

    for project in cc.get_projects():
        if project.name == "Active Sprint":
            active = project
        elif project.name == "Backlog":
            backlog = project

    for column in active.get_columns():
        if column.name == "Done":
            done = column
            break

    return backlog, done


def move_cards(args, github, backlog, done):
    for column in backlog.get_columns():
        logger.log(logging.INFO, f"{backlog.name}: {column.name}")
        for card in column.get_cards():
            if not card.content_url or "/issues/" not in card.content_url:
                continue
            content = card.get_content(content_type="Issue")
            if content.state != "closed":
                continue
            logger.log(logging.INFO, f"  {content.title}")
            try:
                if not args.dryrun:
                    done.create_card(
                        content_id=content.id, content_type="Issue"
                    )
                logger.log(
                    logging.INFO,
                    f"    -> added to Active Sprint: {done.name}",
                )
            except github.GithubException as e:
                if e.data["errors"][0]["message"] != (
                    "Project already has the associated issue"
                ):
                    raise
            if not args.dryrun:
                card.delete()
            logger.log(logging.INFO, "    -> removed.")


def main():
    args = setup()
    github = gh_utils.set_up_github_client()
    cc = gh_utils.get_cc_organization(github)
    backlog, done = get_cards(cc)
    move_cards(args, github, backlog, done)


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
