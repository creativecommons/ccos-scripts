"""
This script pulls the members of the "Community Team Tracking" Asana
project, formats it a bit, then pushes it to a databag
"databags/community_team_list.json"
in creativecommons/creativecommons.github.io-source
"""

# Standard library
import inspect
import logging
import os
import sys

# Third-party
import asana

# First-party/Local
from ccos import log

ASANA_WORKSPACE_GID = "133733285600979"
ASANA_PROJECT_GID = "1172465506923661"

log_name = os.path.basename(os.path.splitext(inspect.stack()[-1].filename)[0])
logger = logging.getLogger(log_name)
log.reset_handler()


def setup_asana_client():
    logger.log(logging.INFO, "Setting up Asana client...")
    try:
        asana_token = os.environ["ADMIN_ASANA_TOKEN"]
    except KeyError:
        logger.critical("missin ADMIN_ASANA_TOKEN environment variable")
        sys.exit(1)
    asana_client = asana.Client.access_token(asana_token)
    try:
        # Perform simple API operation to test authentication
        asana_client.workspaces.get_workspace(ASANA_WORKSPACE_GID)
    except asana.error.NoAuthorizationError as e:
        logger.critical(
            f"{e.status} {e.message} (is ADMIN_ASANA_TOKEN valid?)"
        )
        sys.exit(1)
    logger.log(logging.INFO, "done.")
    return asana_client


def generate_databag(asana_client):
    """
    This method pulls the team members from Asana and
    loads them into the databag after a little
    formatting. The output of this method still needs
    pruning. The databag schema is below.

    databag schema
    {
        "projects": [
            {
                "name": "",
                "repos": "",
                "members": [
                    {
                        "name": "",
                        "role": "",
                        "github: ""
                    },
                    ...
                ]
            },
            ...
        ],
        "community_builders": [
            {
                "name": "",
                "role": "",
                "github: ""
            },
            ...
        ]
    }
    """

    logger.log(logging.INFO, "Pulling from Asana and generating databag...")
    databag = {"projects": [], "community_builders": []}

    members = asana_client.tasks.find_by_section(
        ASANA_PROJECT_GID, opt_fields=["name", "custom_fields"]
    )
    logger.log(logging.INFO, "Team members pulled.")

    logger.log(logging.INFO, "Processing team members...")
    for member in members:
        if member["name"] == "":
            continue  # Sometimes blank names come up
        role = get_custom_field(member, "Role")
        github = get_custom_field(member, "GitHub")
        if role.startswith("Community"):
            databag["community_builders"].append(
                {"name": member["name"], "role": role, "github": github}
            )
        else:
            project_name = get_custom_field(member, "Project Name")
            seen_projects = []

            if project_name not in seen_projects:
                databag["projects"].append(
                    {
                        "name": project_name,
                        "members": [],
                        "repos": get_custom_field(member, "Repo(s)"),
                    }
                )
                seen_projects.append(project_name)

            for project in databag["projects"]:
                if project["name"] == project_name:
                    project["members"].append(
                        {
                            "name": member["name"],
                            "role": role,
                            "github": github,
                        }
                    )
                    break

    logger.log(logging.INFO, "Done.")
    return databag


def sort_databag(databag):
    """
    This function orderes the member according to their roles
    """
    project_priority = {
        "Project Maintainer": 1,
        "Project Core Committer": 2,
        "Project Collaborator": 3,
        "Project Contributor": 4,
    }
    community_builders_priority = {
        "Community Maintainer": 1,
        "Community Collaborator": 2,
    }

    for first_order_key in databag:
        if first_order_key == "projects":
            for project in databag["projects"]:
                member = project["members"]
                member.sort(key=lambda x: x["name"])
                member.sort(key=lambda x: project_priority[x["role"]])

        elif first_order_key == "community_builders":
            community_builder = databag["community_builders"]
            community_builder.sort(key=lambda x: x["name"])
            community_builder.sort(
                key=lambda x: community_builders_priority[x["role"]]
            )
    return databag


def prune_databag(databag):
    """
    Sometimes empty projects find their way into the databag.
    This function prunes out the empty ones.
    """
    pruned = {
        "projects": [],
        "community_builders": databag["community_builders"],
    }

    for project in databag["projects"]:
        if len(project["members"]) > 0:
            pruned["projects"].append(project)

    return pruned


def get_custom_field(task, field_name):
    """
    Gets the value of a custom field
    """
    for field in task["custom_fields"]:
        if field["name"] == field_name:
            if field["type"] == "enum":
                return field["enum_value"]["name"]
            elif field["type"] == "text":
                return field["text_value"]


def get_community_team_data(asana_client):
    return prune_databag(sort_databag(generate_databag(asana_client)))
