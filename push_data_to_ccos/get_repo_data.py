#!/usr/bin/env python3
# vim: set fileencoding=utf-8:

# Third-party
import emoji
import yaml
from github import Github
from github.GithubException import GithubException, UnknownObjectException

# First-party/Local
from push_data_via_git import GITHUB_ORGANIZATION, GITHUB_TOKEN

CC_METADATA_FILE_NAME = ".cc-metadata.yml"


def set_up_github_client():
    print("Setting up GitHub client...")
    github_client = Github(GITHUB_TOKEN)
    return github_client


def get_cc_organization(github_client):
    print("Getting CC's GitHub organization...")
    cc = github_client.get_organization(GITHUB_ORGANIZATION)
    return cc


def get_repositories(organization):
    print("Getting CC's repos...")
    repos = organization.get_repos()
    return repos


def get_repo_github_data(repo):
    print("\tGetting data for this repo...")
    repo_github_data = {
        "id": repo.id,
        "name": repo.name,
        "url": repo.html_url,
        "description": emoji.emojize(repo.description)
        if repo.description
        else "",
        "website": repo.homepage,
        "language": repo.language,
        "created": repo.created_at.isoformat(),
    }
    try:
        license = repo.get_license()
    except UnknownObjectException:
        license = None
    if license:
        repo_github_data["license"] = {
            "name": license.license.name,
            "url": license.html_url,
        }
    else:
        repo_github_data["license"] = None
    return repo_github_data


def get_repo_cc_metadata(repo):
    print("\tGetting CC metadata for this repo...")
    try:
        cc_metadata_file = repo.get_contents(CC_METADATA_FILE_NAME)
    except (UnknownObjectException, GithubException) as e:
        return {}
    cc_metadata = yaml.safe_load(cc_metadata_file.decoded_content)
    if "technologies" in cc_metadata:
        cc_metadata["technologies"] = [
            technology.strip()
            for technology in cc_metadata["technologies"].split(",")
        ]
    return cc_metadata


def get_repo_data_list(repos):
    repo_data_list = []
    count = 1
    total = repos.totalCount

    for repo in repos:
        print(f"Processing {count} of {total} – {repo.name}")
        if not repo.private:
            repo_cc_metadata = get_repo_cc_metadata(repo)
            is_engineering_project = repo_cc_metadata.get(
                "engineering_project", True
            )
            if is_engineering_project:
                repo_github_data = get_repo_github_data(repo)
                if "slack" not in repo_cc_metadata:
                    repo_cc_metadata["slack"] = ""
                repo_data = {**repo_github_data, **repo_cc_metadata}
                repo_data_list.append(repo_data)
            else:
                print("\tNot an active engineering project, skipping")
        count += 1
    return sorted(repo_data_list, key=lambda k: k["name"].lower())


def get_repo_data_dict(repo_data_list):
    # This is needed because Lektor needs a top level object (not array) in the
    # JSON file.
    return {"repos": repo_data_list}


def get_repo_data():
    github_client = set_up_github_client()
    cc = get_cc_organization(github_client)
    repos = get_repositories(cc)
    repo_data_list = get_repo_data_list(repos)
    data = get_repo_data_dict(repo_data_list)
    return data
