"""
This script pulls the members of the Community Team from the databag in the
OS@CC repository, formats it to match the required structure for setting up
GitHub teams and then syncs the teams to GitHub.

This file intentionally has an external API identical to that of
`push_data_to_ccos/get_community_team_data.py`.
"""

# Standard library
import re

# Third-party
import requests

# Constants should match 'push_data_to_ccos/push_data_via_git.py'
GITHUB_ORGANIZATION = "creativecommons"
GITHUB_REPO_NAME = "creativecommons.github.io-source"

# Constants should match 'push_data_to_ccos/sync_data.py'
CT_MEMBERS = "community_team_members.json"

DATABAG_URL = (
    f"https://raw.githubusercontent.com/{GITHUB_ORGANIZATION}/"
    f"{GITHUB_REPO_NAME}/main/databags/{CT_MEMBERS}"
)


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
    print("Pulling from OS@CC...")
    databag = {"projects": []}

    request = requests.get(DATABAG_URL)
    request.raise_for_status()
    projects = request.json()["projects"]
    print("    Team members pulled.")

    print("    Processing team members...")
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

    print("    Done.")
    print("Pull successful.")
    return databag


def get_community_team_data():
    return fetch_databag()
