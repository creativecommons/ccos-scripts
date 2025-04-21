# Standard library
import logging
import re

# Third-party
import requests

# Constants should match 'ccos/data/push_data_via_git.py'
GITHUB_ORGANIZATION = "creativecommons"
GITHUB_REPO_NAME = "ccos-website-source"

# Constants should match 'push_data_to_ccos.py'
CT_MEMBERS = "community_team_members.json"

DATABAG_URL = (
    f"https://raw.githubusercontent.com/{GITHUB_ORGANIZATION}/"
    f"{GITHUB_REPO_NAME}/main/databags/{CT_MEMBERS}"
)

LOG = logging.root


def fetch_databag():
    """
    This method pulls the team members from CCOS and
    and loads them into the databag after a little
    formatting. The databag schema is below.

    databag schema
    {
        "projects": [
            {
                "name": "",
                "repos: [
                    "",
                    ...
                ],
                "members": [
                    {
                        "name": "",
                        "github": ""
                    },
                    ...
                ]
            },
            ...
        ]
    }
    """
    LOG.info("Pulling from OS@CC...")
    databag = {"projects": []}

    request = requests.get(DATABAG_URL)
    request.raise_for_status()
    projects = request.json()["projects"]
    LOG.info("Team members pulled.")

    LOG.info("Processing team members...")
    for project in projects:
        formatted_project = {
            "name": project["name"],
            "repos": re.split(r",\s?", project["repos"]),
            "roles": {},
        }
        members = project["members"]
        for member in members:
            role = member["role"]
            if role not in formatted_project["roles"]:
                formatted_project["roles"][role] = []
            del member["role"]
            formatted_project["roles"][role].append(member)
        databag["projects"].append(formatted_project)

    LOG.success("done.")
    return databag


def get_community_team_data():
    return fetch_databag()
