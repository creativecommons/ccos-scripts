#!/usr/bin/env python3
# vim: set fileencoding=utf-8:
"""
This script gets the data from the Github API to get the names and 
languages of all the repositories of the 'Creative Commons' organization
and generate the required skills.json
"""

# Standard Library
import json
import os
import sys
import logging
import traceback

# Third Party
from github import Github

GITHUB_ORGANIZATION = "creativecommons"
GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]

# Local/library specific
import log

logger = logging.getLogger("sync_community_skills")


class ScriptError(Exception):
    def __init__(self, message, code=None):
        self.code = code if code else 1
        message = "({}) {}".format(self.code, message)
        super(ScriptError, self).__init__(message)


def generate_databag():
    """
    This method pulls the names and languages from the 'PyGithub'
    and loads them into the databag after a little formatting and
    then this databag will be used to generate the required skills.json
    The databag schema is down below:
    databag schema
    {
        "name": "",
        "languages": []
    }
    """
    print("Pulling from OS@CC...")
    github_client = Github(GITHUB_TOKEN)
    cc = github_client.get_organization(GITHUB_ORGANIZATION)
    repos = list(cc.get_repos())
    if not repos:
        raise ScriptError(
            "Unable to setup the Github Client to get the requested"
            f"Github organization and the repos of that organization"
        )
    repos.sort(key=lambda repo: repo.name)
    data = []
    for repo in repos:
        data.append({"name": repo.name, "languages": repo.get_languages()})
    return data


def generate_skills():
    """
    Writing the result array into skills.json file
    """
    print(json.dumps(generate_databag(), indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        generate_skills()
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
