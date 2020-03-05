import datetime
import json
import os
from base64 import b64decode

import git
import yaml
import emoji
from github import Github
from github.GithubException import UnknownObjectException
from cryptography.fernet import Fernet


GIT_USER_NAME = 'CC creativecommons.github.io Bot'
GIT_USER_EMAIL = 'cc-creativecommons-github-io-bot@creativecommons.org'

GITHUB_USERNAME = 'cc-creativecommons-github-io-bot'
GITHUB_ORGANIZATION = 'creativecommons'
GITHUB_REPO_NAME = 'creativecommons.github.io-source'
ENCRYPTED_GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
# Decrypt code should run once and variables stored outside of the function
# handler so that these are decrypted once per container
DECRYPTED_GITHUB_TOKEN = decrypt(ENCRYPTED_GITHUB_TOKEN)
GITHUB_REPO_URL_WITH_CREDENTIALS = f'https://{GITHUB_USERNAME}:{DECRYPTED_GITHUB_TOKEN}@github.com/{GITHUB_ORGANIZATION}/{GITHUB_REPO_NAME}.git'
CC_METADATA_FILE_NAME = '.cc-metadata.yml'

LAMBDA_WORKING_DIRECTORY = '/tmp'
GIT_WORKING_DIRECTORY = f'{LAMBDA_WORKING_DIRECTORY}/{GITHUB_REPO_NAME}'
JSON_FILE_DIRECTORY = f'{GIT_WORKING_DIRECTORY}/databags'

def decrypt(secret):
    key_file = open('key_file', 'rb')
    key = key_file.read()
    key_file.close()
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(secret)


def set_up_repo():
    # Lambda seems to reuse resources sometimes and the clone already exists.
    if not os.path.isdir(GIT_WORKING_DIRECTORY):
        git.Repo.clone_from(url=GITHUB_REPO_URL_WITH_CREDENTIALS, to_path=".")
    git.Remote.pull(GITHUB_REPO_URL_WITH_CREDENTIALS)
    return f'{LAMBDA_WORKING_DIRECTORY}/{GITHUB_REPO_NAME}'


def set_up_git_user():
    os.environ['GIT_AUTHOR_NAME'] = GIT_USER_NAME
    os.environ['GIT_AUTHOR_EMAIL'] = GIT_USER_EMAIL
    os.environ['GIT_COMMITTER_NAME'] = GIT_USER_NAME
    os.environ['GIT_COMMITTER_EMAIL'] = GIT_USER_EMAIL


def set_up_github_client():
    github_client = Github(DECRYPTED_GITHUB_TOKEN)
    return github_client


def get_cc_organization(github_client):
     cc = github_client.get_organization(GITHUB_ORGANIZATION)
     return cc


def get_repositories(organization):
    repos = organization.get_repos()
    return repos


def get_repo_github_data(repo):
    repo_github_data = {
        'id': repo.id,
        'name': repo.name,
        'url': repo.html_url,
        'description': emoji.emojize(repo.description),
        'website': repo.homepage,
        'language': repo.language,
        'created': repo.created_at.isoformat(),
    }
    try:
        license = repo.get_license()
    except UnknownObjectException:
        license = None
    if license:
        repo_github_data['license'] = {
            'name': license.license.name,
            'url': license.html_url
        }
    else:
        repo_github_data['license'] = None
    return repo_github_data


def get_repo_cc_metadata(repo):
    try:
        cc_metadata_file = repo.get_contents(CC_METADATA_FILE_NAME)
    except UnknownObjectException:
        return {}
    cc_metadata = yaml.load(cc_metadata_file.decoded_content)
    if 'technologies' in cc_metadata:
        cc_metadata['technologies'] = [technology.strip() for technology in cc_metadata['technologies'].split(',')]
    return cc_metadata


def get_repo_data_list(repos):
    repo_data_list = []
    count = 1
    total = repos.totalCount

    for repo in repos:
        print(f'Processing {count} of {total} – {repo.name}')
        if not repo.private:
            repo_cc_metadata = get_repo_cc_metadata(repo)
            is_engineering_project = repo_cc_metadata.get('engineering_project', True)
            if is_engineering_project:
                repo_github_data = get_repo_github_data(repo)
                repo_data = {**repo_github_data, **repo_cc_metadata}
                repo_data_list.append(repo_data)
            else:
                print('\tNot an active engineering project, skipping')
        count += 1
    return sorted(repo_data_list, key=lambda k: k['name'].lower()) 


def get_repo_data_dict(repo_data_list):
    # This is needed because Lektor needs a top level object (not array) in the JSON file.
    return {
        'repos': repo_data_list
    }


def generate_json_file(repo_data_dict):
    json_filename = f'{JSON_FILE_DIRECTORY}/repos.json'
    with open(json_filename, 'w') as json_file:
        json.dump(repo_data_dict, json_file, sort_keys=True, indent=4)
    return json_filename


def commit_and_push_changes(json_filename):
    # Leaving this in here because it's useful to test on separate branches sometimes.
    # now = datetime.datetime.now().isoformat()
    # for char in ['-', ':', '.', 'T']:
    #     now = now.replace(char, '_')
    # branch_name = f'{now}_sync'
    # git.exec_command('checkout', f'-b{branch_name}', cwd=GIT_WORKING_DIRECTORY)
    git_diff = git.IndexFile.diff(GIT_WORKING_DIRECTORY)
    if git_diff != (b'', b''):
        repo = git.Repo(GIT_WORKING_DIRECTORY)
        repo.index.add(items=f'{json_filename}')
        repo.index.commit(message='Syncing new repository changes.')
        git.Remote.push(GITHUB_REPO_URL_WITH_CREDENTIALS)


def lambda_handler(*args, **kwargs):
    set_up_repo()
    set_up_git_user()
    github_client = set_up_github_client()
    cc = get_cc_organization(github_client)
    repos = get_repositories(cc)
    repo_data_list = get_repo_data_list(repos)
    repo_data_dict = get_repo_data_dict(repo_data_list)
    json_filename = generate_json_file(repo_data_dict)
    commit_and_push_changes(json_filename)
