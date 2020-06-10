"""
This script pulls the members of the "Community Team Tracking" Asana
project, formats it a bit, then pushes it to a databag
"databags/community_team_list.json" in creativecommons/creativecommons.github.io-source
"""

# Standard Lib
import os
import json

# Third party
import asana
import git
from github import Github

ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
ASANA_PROJECT_GID = "1172465506923661"

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
        ]
    }
    """

    databag = {"projects": []}

    members = ASANA_CLIENT.tasks.find_by_section(
        ASANA_PROJECT_GID, opt_fields=["name", "custom_fields"]
    )
    print("    Team members pulled.")

    print("    Processing team members...")
    for member in members:
        if member["name"] == "":
            continue  # Sometimes blank names come up
        role = get_custom_field(member, "Role")
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
                project["members"].append({"name": member["name"], "role": role})
                break

    print("    Done.")
    return databag


def prune_databag(databag):
    """
    Sometimes empty projects find their way into the databag.
    This function prunes out the empty ones.
    """
    pruned = {"projects": []}

    for project in databag["projects"]:
        if len(project["members"]) > 0:
            pruned["projects"].append(project)

    return pruned


def format_project(role, project, repos):
    """
    Formats data about member roles into a nice pretty string
    """
    return "{} for the {} project{}".format(role, project, format_repo(repos))


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


def generate_json_file(databag):
    print("Generating JSON file...")
    json_filename = f"{JSON_FILE_DIRECTORY}/community_team_members.json"
    with open(json_filename, "w") as json_file:
        json.dump(databag, json_file, sort_keys=True, indent=4)
    return json_filename


def commit_and_push_changes(json_filename):
    repo = git.Repo(GIT_WORKING_DIRECTORY)
    git_diff = repo.index.diff(None)
    if git_diff != []:
        repo.index.add(items=f"{json_filename}")
        repo.index.commit(message="Syncing new community team changes.")
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
    """
    Pushes the generated databag to GitHub
    """
    json_filename = generate_json_file(databag)
    commit_and_push_changes(json_filename)


print("Pulling from Asana and generating databag...")
databag = prune_databag(generate_databag())
print("Pull successful.")

print("Pushing page content to open source repo...")
set_up_repo()
set_up_git_user()
push_data = push_to_repo(databag)
print("Pushed successfully.")
