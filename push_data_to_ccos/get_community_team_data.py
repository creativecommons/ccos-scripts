"""
This script pulls the members of the "Community Team Tracking" Asana
project, formats it a bit, then pushes it to a databag
"databags/community_team_list.json"
in creativecommons/creativecommons.github.io-source
"""

# Standard Lib
import logging
import os

# Third party
import asana

from normalize_repos import log

ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
ASANA_PROJECT_GID = "1172465506923661"
log.set_up_logging()
logger = logging.getLogger("push_data_to_ccos")
log.reset_handler()


def generate_databag():
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

    members = ASANA_CLIENT.tasks.find_by_section(
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
    logger.log(log.SUCCESS, "Pull successful.")
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
        "Community Collaborator": 1,
        "Community Contributor": 2,
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


def get_community_team_data():
    return prune_databag(sort_databag(generate_databag()))
