#!/usr/bin/env python3
# vim: set fileencoding=utf-8:
# Standard library
import json
import os

# Third-party
import git

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


def generate_json_file(data, filename):
    print("Generating JSON file...")
    json_filename = f"{JSON_FILE_DIRECTORY}/{filename}"
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)
    return json_filename


def commit_and_push_changes(json_filename):
    repo = git.Repo(GIT_WORKING_DIRECTORY)
    git_diff = repo.index.diff(None)
    if git_diff:
        repo.index.add(items=f"{json_filename}")
        repo.index.commit(message="Syncing new data changes.")
        origin = repo.remotes.origin
        print("Pushing latest code...")
        origin.push()
    else:
        print("No changes to push...")


def push_data(data, filename):
    set_up_repo()
    set_up_git_user()
    json_filename = generate_json_file(data, filename)
    commit_and_push_changes(json_filename)
