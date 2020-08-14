import os
import re

# Third party
from github import Github, UnknownObjectException

GITHUB_ORGANIZATION = "creativecommons"
GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]


def set_up_github_client():
    print("Setting up GitHub client...")
    github_client = Github(GITHUB_TOKEN)
    return github_client


def get_cc_organization(github_client):
    print("Getting CC's GitHub organization...")
    cc = github_client.get_organization(GITHUB_ORGANIZATION)
    return cc


def create_teams_for_data(databag, client=None, organization=None):
    if client is None:
        client = set_up_github_client()
    if organization is None:
        organization = get_cc_organization(client)

    print("Creating and populating teams...")
    projects = databag['projects']
    for project in projects:
        project_name = project['name']
        print(f"    Creating and populating teams for project {project_name}...")
        repos = project['repos']
        roles = project['roles']
        for role, members in roles.items():
            members = [member['github'] for member in members]
            print("        Finding team...")
            team = map_role_to_team(organization, project_name, role)
            print("        Done.")
            print("        Populating repos...")
            map_team_to_repos(organization, team, repos, True)
            print("        Done.")
            print("        Populating members...")
            map_team_to_members(client, team, members, True)
            print("        Done.")
        print("    Done.")
    print("Done.")


def map_team_to_members(client, team, final_user_logins, non_destructive=False):
    """
    Map the team to the given set of members. Any members that are not already
    a part of the team will be added and any additional members that are a part
    of the team will be removed, unless chosen not to.

    @param client: the GitHub client
    @param team: the Team object representing the team
    @param final_user_logins: the list of users to associate with the team
    @param non_destructive: whether to trim extra repos or preserve them
    """
    initial_users = team.get_members()
    initial_user_logins = [user.login for user in initial_users]

    if not non_destructive:
        users_to_drop = [
            member
            for member in initial_users
            if member.login not in final_user_logins
        ]
        for user in users_to_drop:
            team.remove_membership(user)

    users_to_add = [
        client.get_user(login)
        for login in final_user_logins
        if login not in initial_user_logins
    ]
    for user in users_to_add:
        team.add_membership(user)


def map_team_to_repos(organization, team, final_repo_names, non_destructive=False):
    """
    Map the team to the given set of repositories. Any repositories that are
    not already a part of the team will be added and any additional repositories
    that are a part of the team will be removed, unless chosen not to.

    @param organization: the Organisation object of which the team is a part
    @param team: the Team object representing the team
    @param final_repo_names: the list of repo names to associate with the team
    @param non_destructive: whether to trim extra repos or preserve them
    """
    initial_repos = team.get_repos()
    initial_repo_names = [repo.name for repo in initial_repos]

    if not non_destructive:
        repos_to_drop = [
            repo
            for repo in initial_repos
            if repo.name not in final_repo_names
        ]
        for repo in repos_to_drop:
            team.remove_from_repos(repo)

    repos_to_add = [
        organization.get_repo(repo_name)
        for repo_name in final_repo_names
        if repo_name not in initial_repo_names
    ]
    for repo in repos_to_add:
        team.add_to_repos(repo)


def map_role_to_team(organization, project_name, role):
    """
    Map the given role in the given project to a team. Creates the team if one
    such does not already exist.

    @param organization: the Organisation object of which the team is a part
    @param project_name: the name of the project to which the team belongs
    @param role: the role held by folks in the team
    @return: the team associated with the role
    """
    team_slug, team_name = get_team_slug_name(project_name, role)
    try:
        team = organization.get_team_by_slug(team_slug)
        print("            Team exists, will update.")
    except UnknownObjectException:
        print("            Did not exist, creating...")
        description = (f'Community Team for {project_name} '
                       f'containing folks with the role "{role}"')
        team = organization.create_team(
            name=team_name,
            description=description,
            privacy='closed'
        )
        print("            Done.")
    return team


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
    team_name = f"CT: {project_name} {pluralized(role)}"
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
    defined_plurals = {
        "person": "people"
    }
    if word in defined_plurals:
        return defined_plurals[word]

    es_endings = ['s', 'sh', 'ch', 'x', 'z']
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
