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
import git
from github import Github


ASANA_ROADMAP_PROJECT_GID = "1140559033201049"
ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])

GIT_USER_NAME = "CC creativecommons.github.io Bot"
GIT_USER_EMAIL = "cc-creativecommons-github-io-bot@creativecommons.org"

GITHUB_USERNAME = "cc-creativecommons-github-io-bot"
GITHUB_ORGANIZATION = "creativecommons"
GITHUB_REPO_NAME = "creativecommons.github.io-source"

GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]
GITHUB_REPO_URL_WITH_CREDENTIALS = (
    f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}"
    f"@github.com/{GITHUB_ORGANIZATION}/{GITHUB_REPO_NAME}.git"
)

WORKING_DIRECTORY = "/tmp"
GIT_WORKING_DIRECTORY = f"{WORKING_DIRECTORY}/{GITHUB_REPO_NAME}"
JSON_FILE_DIRECTORY = f"{GIT_WORKING_DIRECTORY}/databags"


def set_up_repo():
    if not os.path.isdir(GIT_WORKING_DIRECTORY):
        print("Cloning repo...")
        repo = git.Repo.clone_from(
            url=GITHUB_REPO_URL_WITH_CREDENTIALS, to_path=GIT_WORKING_DIRECTORY
        )
    else:
        print("Setting up repo...")
        repo = git.Repo(GIT_WORKING_DIRECTORY)
    origin = repo.remotes.origin
    print("Pulling latest code...")
    origin.pull()
    return f"{WORKING_DIRECTORY}/{GITHUB_REPO_NAME}"


def set_up_git_user():
    print("Setting up git user...")
    os.environ["GIT_AUTHOR_NAME"] = GIT_USER_NAME
    os.environ["GIT_AUTHOR_EMAIL"] = GIT_USER_EMAIL
    os.environ["GIT_COMMITTER_NAME"] = GIT_USER_NAME
    os.environ["GIT_COMMITTER_EMAIL"] = GIT_USER_EMAIL


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


def generate_json_file(databag):
    print("Generating JSON file...")
    json_filename = f"{JSON_FILE_DIRECTORY}/search_roadmap.json"
    with open(json_filename, "w") as json_file:
        json.dump(databag, json_file, sort_keys=True, indent=4)
    return json_filename


def commit_and_push_changes(json_filename):
    repo = git.Repo(GIT_WORKING_DIRECTORY)
    git_diff = repo.index.diff(None)
    if git_diff != []:
        repo.index.add(items=f"{json_filename}")
        repo.index.commit(message="Syncing new search roadmap changes.")
        origin = repo.remotes.origin
        print("Pushing latest code...")
        try:
            origin.push()
        except Exception as e:
            print(f"Got exception {e} \n Trying manual push...")
            g = git.Git(GIT_WORKING_DIRECTORY)
            print(g.execute(["git", "push", f"{GITHUB_REPO_URL_WITH_CREDENTIALS}", "master"]))
    else:
        print("No changes to push...")


def push_to_repo(databag):
    json_filename = generate_json_file(databag)
    commit_and_push_changes(json_filename)


print("Pulling from Asana...")
databag = generate_databag()
print("Pull successful.")

print("Pushing page content to open source repo...")
set_up_repo()
set_up_git_user()
push_data = push_to_repo(databag)
print("Pushed successfully.")
