# Standard library
import logging

# Third-party
import emoji
import yaml
from github.GithubException import GithubException, UnknownObjectException

CC_METADATA_FILE_NAME = ".cc-metadata.yml"
LOG = logging.root


def get_repositories(organization):
    LOG.info("Getting CC's repos...")
    repos = organization.get_repos()
    return repos


def get_repo_github_data(repo):
    LOG.info("Getting data for this repo...")
    repo_github_data = {
        "id": repo.id,
        "name": repo.name,
        "url": repo.html_url,
        "description": (
            emoji.emojize(repo.description) if repo.description else ""
        ),
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
    LOG.info("Getting CC metadata for this repo...")
    try:
        cc_metadata_file = repo.get_contents(CC_METADATA_FILE_NAME)
    except (UnknownObjectException, GithubException):
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
        LOG.info(f"Processing {count} of {total} – {repo.name}")
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
                LOG.info("Not an active engineering project, skipping")
        count += 1
    return sorted(repo_data_list, key=lambda k: k["name"].lower())


def get_repo_data_dict(repo_data_list):
    # This is needed because Lektor needs a top level object (not array) in the
    # JSON file.
    return {"repos": repo_data_list}


def get_repo_data(gh_org_cc):
    repos = get_repositories(gh_org_cc)
    repo_data_list = get_repo_data_list(repos)
    data = get_repo_data_dict(repo_data_list)
    return data


def get_repo_names(gh_org_cc):
    repos = get_repositories(gh_org_cc)
    names = []
    for repo in repos:
        names.append(repo.name)
    return names
