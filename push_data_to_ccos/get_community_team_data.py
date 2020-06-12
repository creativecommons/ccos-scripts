"""
This script pulls the members of the "Community Team Tracking" Asana
project, formats it a bit, then pushes it to a databag
"databags/community_team_list.json"
in creativecommons/creativecommons.github.io-source
"""

# Standard Lib
import os

# Third party
import asana


ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
ASANA_PROJECT_GID = "1172465506923661"


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
                        "role": ""
                    },
                    ...
                ]
            },
            ...
        ],
        "community_builders": [
            {
                "name": "",
                "role": ""
            },
            ...
        ]
    }
    """
    print("Pulling from Asana and generating databag...")
    databag = {"projects": [], "community_builders": []}

    members = ASANA_CLIENT.tasks.find_by_section(
        ASANA_PROJECT_GID, opt_fields=["name", "custom_fields"]
    )
    print("    Team members pulled.")

    print("    Processing team members...")
    for member in members:
        if member["name"] == "":
            continue  # Sometimes blank names come up
        role = get_custom_field(member, "Role")
        if role.startswith("Community"):
            databag["community_builders"].append(
                {"name": member["name"], "role": role}
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
                        {"name": member["name"], "role": role}
                    )
                    break

    print("    Done.")
    print("Pull successful.")
    return databag


def prune_databag(databag):
    """
    Sometimes empty projects find their way into the databag.
    This function prunes out the empty ones.
    """
    pruned = {"projects": [], "community_builders": databag["community_builders"]}

    for project in databag["projects"]:
        if len(project["members"]) > 0:
            pruned["projects"].append(project)

    return pruned


def get_custom_field(task, field_name):
    """
    Gets the value of a custom field
    """
    for field in task["custom_fields"]:
        if field["name"] == "Repo(s)" and field_name == "Repo(s)":
            return field["text_value"]
        elif field["name"] == field_name:
            if field["enum_value"]:
                return field["enum_value"]["name"]
            return None


def get_community_team_data():
    return prune_databag(generate_databag())
