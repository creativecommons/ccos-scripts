"""
This script gets the data from the Github API to get the names and 
languages of all the repositories of the 'Creative Commons' orgaization
and generate the required skills.json
"""

# Standard Lib
import json
import os


# Third Part
import requests

GIT_USER_NAME = "CC creativecommons.github.io Bot"
GIT_USER_EMAIL = "cc-creativecommons-github-io-bot@creativecommons.org"

GITHUB_USERNAME = "cc-creativecommons-github-io-bot"
GITHUB_ORGANIZATION = "creativecommons"
GITHUB_REPO_NAME = "ccos-scripts"

GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]
GITHUB_REPO_URL_WITH_CREDENTIALS = (
    f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}"
    f"@github.com/{GITHUB_ORGANIZATION}/{GITHUB_REPO_NAME}.git"
)


def generate_databag():
    """
    This method pulls the names and languages from the 'Github Api'
    and loads them into the databag after a little formatting and
    then this databag will be used to generate the required skills.json
    The databag schema is down below:
    databag schema
    {
        "name": "",
        "languages": []
    }
    """
    print("Pulling from the Github API")
    result = []
    api_request = requests.get(
        "https://api.github.com/orgs/creativecommons/repos?per_page=100"
    )
    data = api_request.json()
    for x in data:
        databag = {"name": "", "languages": []}
        databag["name"] = x["name"]
        result.append(databag)
        languages_dat_from_api = requests.get(x["languages_url"])
        databag["languages"].append(languages_dat_from_api.json())
    return result


"""
Writing the result array into skills.json file
"""

with open("skills.json", "w") as outfile:
    json.dump(generate_databag(), outfile)
