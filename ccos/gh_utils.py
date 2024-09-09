# Standard library
import logging
import os
import re
import sys

# Third-party
from github import Github
from github.GithubException import BadCredentialsException
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.requests import log as gql_requests_log
from urllib3.util.retry import Retry

GITHUB_ORGANIZATION = "creativecommons"
GITHUB_RETRY_STATUS_FORCELIST = [
    408,  # Request Timeout
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
]
GITHUB_USERNAME_DEFAULT = "cc-creativecommons-github-io-bot"
LOG = logging.root
gql_requests_log.setLevel(logging.WARNING)


def get_credentials():
    try:
        github_token = os.environ["ADMIN_GITHUB_TOKEN"]
    except KeyError:
        LOG.critical("missing ADMIN_GITHUB_TOKEN environment variable")
        sys.exit(1)
    try:
        github_username = os.environ["ADMIN_GITHUB_USERNAME"]
    except KeyError:
        github_username = GITHUB_USERNAME_DEFAULT
    return github_username, github_token


def gql_query(query):
    return gql(query)


def setup_github_rest_client():
    _, github_token = get_credentials()
    LOG.info("Setting up GitHub Rest API client")
    # TODO: Remove retry parameter (urllib3.util.retry.Retry object) once we
    # are using PyGithub v2.0
    # https://github.com/creativecommons/ccos-scripts/issues/179
    retry = Retry(
        # try again after 5, 10, 20, 40, 80 seconds
        # for specified HTTP status codes
        total=5,
        backoff_factor=10,
        status_forcelist=GITHUB_RETRY_STATUS_FORCELIST,
        allowed_methods={
            "DELETE",
            "GET",
            "HEAD",
            "OPTIONS",
            "POST",
            "PUT",
            "TRACE",
        },
    )
    github_rest_client = Github(login_or_token=github_token, retry=retry)
    return github_rest_client


def setup_github_gql_client():
    _, github_token = get_credentials()
    LOG.info("Setting up GitHub GraphQL API client")
    transport = RequestsHTTPTransport(
        url="https://api.github.com/graphql",
        headers={"Authorization": f"bearer {github_token}"},
        timeout=10,
        retries=5,
        retry_backoff_factor=10,
        retry_status_forcelist=GITHUB_RETRY_STATUS_FORCELIST,
    )
    with open("ccos/schema.docs.graphql") as file_obj:
        gh_schema = file_obj.read()
    github_gql_client = Client(transport=transport, schema=gh_schema)
    return github_gql_client


def get_cc_organization(github_client=None):
    if github_client is None:
        github_client = setup_github_rest_client()
    LOG.info("Getting CC's GitHub organization...")
    try:
        gh_org_cc = github_client.get_organization(GITHUB_ORGANIZATION)
    except BadCredentialsException as e:
        LOG.critical(
            f"{e.status} {e.data['message']} (see"
            f" {e.data['documentation_url']})"
        )
        sys.exit(1)
    LOG.success("done.")
    return gh_org_cc


def get_select_repos(args, gh_org_cc=None):
    if gh_org_cc is None:
        gh_org_cc = get_cc_organization()
    LOG.info("Get select GitHub repositories")
    LOG.change_indent(-1)
    repos = list(gh_org_cc.get_repos())
    LOG.change_indent(+1)
    # Skip archived repos
    repos_selected = []
    for repo in repos:
        if not repo.archived:
            repos_selected.append(repo)
    repos = repos_selected
    # Skip non-selected repos
    if args.repos:
        repos_selected = []
        for repo in repos:
            if repo.name in args.repos:
                repos_selected.append(repo)
        repos = repos_selected
        if not repos:
            raise Exception(
                "Specified repositories do not include any valid"
                f" repositories: {args.repos}"
            )
    repos.sort(key=lambda repo: repo.name)
    return repos


def get_team_slug_name(project_name, role):
    """
    Get the team name and team slug based on GitHub's naming scheme. By
    convention, teams are named in a well-defined .

    team name schema
    CT: <project name> <role, pluralized>

    team slug schema
    ct-<project_name_slug>-<role_slug>

    @param project_name: the name of the project to which the team belongs
    @param role: the role held by folks in the team
    @return: the slug and name of the team
    """
    sanitized_role = pluralized(role).replace("Project ", "")
    team_name = f"CT: {project_name} {sanitized_role}"
    team_slug = slugified(team_name)
    return team_slug, team_name


def pluralized(word):
    """
    Get the plural of the given word. Contains a dictionary for non-standard
    plural forms. If the word ends in one of 5 known endings, appends an 'es'
    to the end. By default, just appends an 's' to the given word.

    @param word: the word to pluralize
    @return: the plural form of the noun
    """
    defined_plurals = {"person": "people"}
    if word in defined_plurals:
        return defined_plurals[word]

    es_endings = ["s", "sh", "ch", "x", "z"]
    if any([word.endswith(ending) for ending in es_endings]):
        return f"{word}es"
    else:
        return f"{word}s"


def slugified(text):
    """
    Get the slug generated from the given text. Replaces all non-alphanumeric
    characters with hyphens. Coalesces successive hyphens into one.

    @param text: the text to slugify
    @return: the slug made from the given text
    """
    return re.sub("-+", "-", re.sub(r"\W", "-", text.lower()))
