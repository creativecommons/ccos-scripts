# Standard library
import json
import logging
import os
from tempfile import TemporaryDirectory

# Third-party
import git

# First-party/Local
from ccos.gh_utils import GITHUB_ORGANIZATION, get_credentials

GITHUB_REPO_NAME = "creativecommons.github.io-source"
GIT_USER_EMAIL = "cc-creativecommons-github-io-bot@creativecommons.org"
GIT_USER_NAME = "CC creativecommons.github.io Bot"
JSON_FILE_DIR = "databags"
LOG = logging.root


def set_up_repo(git_working_dir):
    github_username, github_token = get_credentials()
    github_repo_url_with_credentials = (
        f"https://{github_username}:{github_token}"
        f"@github.com/{GITHUB_ORGANIZATION}/{GITHUB_REPO_NAME}.git"
    )
    if not os.path.isdir(git_working_dir):
        LOG.info("Cloning repo...")
        repo = git.Repo.clone_from(
            url=github_repo_url_with_credentials, to_path=git_working_dir
        )
    else:
        LOG.info("Setting up repo...")
        repo = git.Repo(git_working_dir)
    origin = repo.remotes.origin
    LOG.info("Pulling latest code...")
    origin.pull()


def set_up_git_user():
    LOG.info("Setting up git user...")
    os.environ["GIT_AUTHOR_NAME"] = GIT_USER_NAME
    os.environ["GIT_AUTHOR_EMAIL"] = GIT_USER_EMAIL
    os.environ["GIT_COMMITTER_NAME"] = GIT_USER_NAME
    os.environ["GIT_COMMITTER_EMAIL"] = GIT_USER_EMAIL


def generate_json_file(git_working_dir, data, filename):
    LOG.info("Generating JSON file...")
    json_filename = os.path.join(git_working_dir, JSON_FILE_DIR, filename)
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4)
    return json_filename


def commit_and_push_changes(git_working_dir, json_filename):
    repo = git.Repo(git_working_dir)
    git_diff = repo.index.diff(None)
    if git_diff:
        repo.index.add(items=f"{json_filename}")
        repo.index.commit(message="Syncing new data changes.")
        origin = repo.remotes.origin
        LOG.info("Pushing latest code...")
        origin.push()
    else:
        LOG.info("No changes to push...")


def push_data(data, filename):
    with TemporaryDirectory() as temp_dir:
        git_working_dir = os.path.join(temp_dir, GITHUB_REPO_NAME)
        set_up_repo(git_working_dir)
        set_up_git_user()
        json_filename = generate_json_file(git_working_dir, data, filename)
        commit_and_push_changes(git_working_dir, json_filename)
