# Standard library
import logging
import sys

LOG = logging.root


def generate_databag(team_members):
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
    databag = {"projects": [], "community_builders": []}
    LOG.info("Processing team members...")
    for member in team_members:
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

    LOG.success("done.")
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


def verify_databag(databag, repo_names):
    """
    Ensure all repository names are accurate.
    """
    for project in databag["projects"]:
        databag_repos = project["repos"].split(",")
        for databag_repo in databag_repos:
            if databag_repo not in repo_names:
                LOG.error(
                    f'"{project["name"]}" contains invalid reposiotry:'
                    f' "{databag_repo}"',
                )
                sys.exit(1)
    return databag


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


def get_community_team_data(team_members, repo_names):
    databag = generate_databag(team_members)
    databag = prune_databag(databag)
    databag = verify_databag(databag, repo_names)
    databag = sort_databag(databag)
    return databag
