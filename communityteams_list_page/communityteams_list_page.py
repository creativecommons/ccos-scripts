"""
This script pulls the members of the "Community Team Tracking" Asana
project, formats it a bit, then pushes it to a databag
"databags/communityteams_list.json" in creativecommons/creativecommons.github.io-source
"""

# Standard Lib
import os
import json

# Third party
import asana
from github import Github

ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
ASANA_PROJECT_GID = "1172465506923661"

GITHUB_CLIENT = Github(os.environ["ADMIN_GITHUB_TOKEN"])

"""
databag schema
{
    "team_members": [
        {
            "name": "",
            "projects": [
                "",
                ""
            ]
        },
        ...
    ]
}
"""
def generate_databag():
    databag = {
        "team_members": []
    }

    tasks = ASANA_CLIENT.tasks.find_by_section(
        ASANA_PROJECT_GID,
        opt_fields=["name", "custom_fields"]
    )
    print("    Team members pulled.")

    members_seen = []

    print("    Processing team members...")
    for task in tasks:
        if task["name"] == "": continue # Sometimes blank names come up
        role = get_custom_field(task, "Role")
        project_name = get_custom_field(task, "Project Name")
        repos = get_custom_field(task, "Repo(s)")

        # If the member has different roles in different projects
        # then we"ve seen them before, so instead of adding a new
        # member, add the new project
        if task["name"] in members_seen:
            print("    Member "{}" already seen, appending to projects".format(task["name"]))
            for member in databag["team_members"]:
                if task["name"] == member["name"]: # Find member data in databag
                    member["projects"].append( # Add project line to projects
                        format_project(
                            role,
                            project_name,
                            repos
                        )
                    )
                    break
        else: # If not seen before
            member = {
                "name": task["name"],
                "projects": [
                    format_project(
                        role,
                        project_name,
                        repos
                    )
                ]
            }
            databag["team_members"].append(member)

        members_seen.append(task["name"])
    print("    Done.")

    return databag


"""
Formats data about member roles into a nice pretty string
"""
def format_project(role, project, repos):
    return "{} for the {} project{}".format(
        role,
        project,
        format_repo(repos)
    )

"""
The formatting for the repo part of the project string needs a
little extra doing, this function does that doing.
"""
def format_repo(repos):
    base = ", has privileges for the {} {}"
    if repos is None:
        return ""
    else:
        return base.format(
            repos,
            "repository" if len(repos.split(",")) == 1 else "repositories"
        )

"""
Gets the value of a custom field
"""
def get_custom_field(task, field_name):
    for field in task["custom_fields"]:
        if field["name"] == "Repo(s)" and field_name == "Repo(s)":
            return field["text_value"]
        elif field["name"] == field_name:
            return field["enum_value"]["name"]

"""
Pushes the generated databag to GitHub
"""
def push_to_repo(databag):
    oss_repo = GITHUB_CLIENT.get_repo("creativecommons/creativecommons.github.io-source")
    update = oss_repo.update_file(
        path="databags/communityteams_list.json",
        message="Update Community Teams List Databag",
        content=json.dumps(databag),
        sha=oss_repo.get_contents("databags/communityteams_list.json").sha,
        branch="master"
    )
    return update

print("Pulling from Asana and generating databag...")
databag = generate_databag()
print("Pull successful.")

print("Pushing page content to open source repo...")
push_data = push_to_repo(databag)
print("Pushed successfully. Commit Info: {}".format(push_data))