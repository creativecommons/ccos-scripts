#!/usr/bin/env python3

"""
This script removes all Hacktoberfest issues labels and related repository
topics.
"""

# Standard library
import argparse
import sys
import traceback

# Third-party
from github import UnknownObjectException

# First-party/Local
import ccos.log
from ccos import gh_utils

LOG = ccos.log.setup_logger()


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
    args = ap.parse_args()
    return args


def remove_hacktoberfest_label(repos):
    for repo in repos:
        try:
            hacktober_label = repo.get_label("Hacktoberfest")
        except UnknownObjectException:
            continue
        hacktober_label.delete()
        LOG.info(f"{repo.name}: deleted issues label: Hacktoberfest")


def remove_hacktoberfest_topic(repos):
    for repo in repos:
        old_topics = repo.get_topics()
        old_topics.sort()
        new_topics = []
        hacktober_topics = []
        for topic in old_topics:
            if "hacktober" not in topic.lower():
                new_topics.append(topic)
            else:
                hacktober_topics.append(topic)
        new_topics.sort()
        hacktober_topics.sort()
        hacktober_topics = ", ".join(hacktober_topics)
        if old_topics != new_topics:
            repo.replace_topics(new_topics)
            LOG.info(
                f"{repo.name}: removed Hacktoberfest related topics:"
                f" {hacktober_topics}"
            )


def main():
    args = setup()
    LOG.info("Starting normalization")
    repos = gh_utils.get_select_repos(args)
    remove_hacktoberfest_label(repos)
    remove_hacktoberfest_topic(repos)


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
    except KeyboardInterrupt:
        LOG.info("Halted via KeyboardInterrupt.")
        sys.exit(130)
    except Exception:
        LOG.error(f"Unhandled exception: {traceback.format_exc()}")
        sys.exit(1)
