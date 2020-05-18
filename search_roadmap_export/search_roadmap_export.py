"""
This script pulls selected tasks from the CC Search Roadmap Asana project, then
fills that information into a lektor databag, and pushes it to a file in
creativecommons/creativecommons.github.io-source.
"""

# Standard Library
import os
import json
import re

# Third-party
import asana
from github import Github

ASANA_ROADMAP_PROJECT_GID = "1140559033201049"

ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
GITHUB_CLIENT = Github(os.environ["ADMIN_GITHUB_TOKEN"])


def fetch_quarters():
    """
    This method fetches all sections in the roadmap project, then
    using some regex magic, filters out all sections that are not
    named like quarter names. For example:

    Q1 2020
    q1 2021
    q3 2020

    are all matches.
    """
    sections = ASANA_CLIENT.sections.find_by_project(ASANA_ROADMAP_PROJECT_GID)
    for section in sections:
        if re.match("Q\d{1}\s\d{4}", section["name"], re.IGNORECASE):
            yield {"name": section["name"], "gid": section["gid"]}


def generate_databag():
    """
    databag schema
    {
        "quarters": [
            {
                "name": "Q1 2020",
                "tasks": [
                    {
                        "gid": "",
                        "name": "",
                        "description": ""
                    },
                    ...
                ]
            },
            {
                "name": "Q2 2020",
                "tasks": []
            },
            ...
        ]
    }

    """
    databag = {"quarters": []}

    print("Generating Databag...")
    for quarter in fetch_quarters():
        print("    Pulling tasks for quarter - {}...".format(quarter["name"]))
        tasks = ASANA_CLIENT.tasks.find_by_section(  # Get tasks in section
            quarter["gid"],
            opt_fields=["name", "custom_fields", "tags.name", "completed"],
        )
        print("    Done.")
        quarter = {"name": quarter["name"], "tasks": []}

        print("    Processing tasks...")
        for task in tasks:
            # if task does not have opt out flag, and is not complete
            if has_filtering_tag(task) and not task["completed"]:
                quarter["tasks"].append(
                    {
                        "gid": task["gid"],
                        "name": task["name"],
                        "description": get_public_description(task),
                    }
                )
        print("    Done.")

        databag["quarters"].append(quarter)

    print("    Pruning quarters...")  # remove quarter if it has no tasks
    databag["quarters"] = [
        quarter for quarter in databag["quarters"] if len(quarter["tasks"]) != 0
    ]
    print("    Done.")

    return databag


def has_filtering_tag(task):
    """
    Indicates if an Asana task has the opt-out tag
    """
    for tag in task["tags"]:
        if tag["name"] == "roadmap_ignore":
            return False
        return True


def get_public_description(task):
    """
    Gets the Public Description field of an Asana Task
    """
    for field in task["custom_fields"]:
        if field["name"] == "Public Description":
            return field["text_value"]


def push_to_repo(databag):
    oss_repo = GITHUB_CLIENT.get_repo(
        "creativecommons/creativecommons.github.io-source"
    )
    update = oss_repo.update_file(
        path="databags/search_roadmap.json",
        message="Update Search Roadmap Databag",
        content=json.dumps(databag),
        sha=oss_repo.get_contents("databags/search_roadmap.json").sha,
        branch="master",
    )
    return update


print("Pulling from Asana...")
databag = generate_databag()
print("Pull successful.")

print("Pushing page content to open source repo...")
push_data = push_to_repo(databag)
print("Pushed successfully. Commit Info: {}".format(push_data))
