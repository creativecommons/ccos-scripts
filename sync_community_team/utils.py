import os
import re
import sys

# Third party
from github import Github
sys.path.append((os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
+ '/utils/'))
from github_utils import get_cc_organization, set_up_github_client


def set_up_github_client():
    return github_utils.set_up_github_client()
    

def get_cc_organization(github_client):
    return github_utils.get_cc_organization(github_client)


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
    defined_plurals = {
        "person": "people"
    }
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