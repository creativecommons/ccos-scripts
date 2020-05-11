"""
This script pulls selected tasks from the CC Search Roadmap Asana project, then
fills that information into a lektor databag, and pushes it to a file in
creativecommons/creativecommons.github.io-source.
"""

# Standard Library
import os
import json

# Third-party
import asana
from github import Github

ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
ASANA_GIDS = { # GIDs are unique IDs for Asana resources, each task, tag, project, section, etc. has one.
    'ROADMAP_SECTIONS': {
        # No Q1 section because all tasks are completed
        'Q2 2020': '1144184402700458',
        'Q3 2020': '1144184404806427',
        'Q4 2020': '1144184406321401'
    }
}

GITHUB_CLIENT = Github(os.environ["ADMIN_GITHUB_TOKEN"])

"""
databag schema
{
    "quarters": [
        {
            "name": "Q1 2020",
            "tasks": [
                {
                    "gid": "",
                    "name": "",
                    "description": ""
                },
                ...
            ]
        },
        {
            "name": "Q2 2020",
            "tasks": []
        },
        ...
    ]
}

"""
def generate_databag():
    databag = {
        "quarters": []
    }

    print('Generating Databag...')
    for section_name, section_gid in ASANA_GIDS['ROADMAP_SECTIONS'].items(): # for section in included sections
        print('    Pulling tasks for quarter - {}...'.format(section_name))
        tasks = ASANA_CLIENT.tasks.find_by_section( # Get tasks in section
            ASANA_GIDS['ROADMAP_SECTIONS'][section_name],
            opt_fields=['name', 'custom_fields', 'tags.name', 'completed']
        )
        print('    Done.')
        quarter = {
            "name": section_name,
            "tasks": []
        }

        print('    Processing tasks...')
        for task in tasks:
            # if task does not have opt out flag, and is not complete
            if has_filtering_tag(task) and not task['completed']:
                quarter['tasks'].append({
                    'gid': task['gid'],
                    'name': task['name'],
                    'description': get_public_description(task)
                })
        print('    Done.')

        databag['quarters'].append(quarter)

    print('    Pruning quarters...') # remove quarter if it has no tasks
    databag['quarters'] = [quarter for quarter in databag['quarters'] if len(quarter['tasks']) != 0]
    print('    Done.')

    return databag

"""
Indicates if an Asana task has the opt-out tag
"""
def has_filtering_tag(task):
    for tag in task['tags']:
        if tag['name'] == 'roadmap_ignore':
            return False
        return True

"""
Gets the Public Description field of an Asana Task
"""
def get_public_description(task):
    for field in task['custom_fields']:
        if field['name'] == 'Public Description':
            return field['text_value']

def push_to_repo(databag):
    oss_repo = GITHUB_CLIENT.get_repo("creativecommons/creativecommons.github.io-source")
    update = oss_repo.update_file(
        path="databags/search_roadmap.json",
        message="Update Search Roadmap Databag",
        content=json.dumps(databag),
        sha=oss_repo.get_contents("databags/search_roadmap.json").sha,
        branch="master"
    )
    return update

print("Pulling from Asana...")
databag = generate_databag()
print("Pull successful.")

print("Pushing page content to open source repo...")
push_data = push_to_repo(databag)
print("Pushed successfully. Commit Info: {}".format(push_data))
