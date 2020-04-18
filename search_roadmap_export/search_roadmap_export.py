"""
This script pulls selected tasks from the CC Search Roadmap Asana project, then
fills that information into a lektor template, and pushes it to a file in
creativecommons/creativecommons.github.io-source.
"""

# Standard Library
import os
import json

# Third-party
import asana
from github import Github

from config import CONFIG

ASANA_CLIENT = asana.Client.access_token(os.environ["ASANA_TOKEN"])

"""
RETURN SCHEMA:

{
    'Q12020': [
        {
            'gid': '...',
            'name': '...',
            'public_description: '...'
        },
        ...
    ],
    ...
}

"""
def tasks_by_section():
    sections = {
        'Q12020': [],
        'Q22020': [],
        'Q32020': [],
        'Q42020': []
    }

    for section_name, section_gid in CONFIG['ROADMAP_SECTIONS'].items(): # for section in included sections
        tasks = ASANA_CLIENT.tasks.find_by_section(
            CONFIG['ROADMAP_SECTIONS'][section_name],
            opt_fields=['name', 'custom_fields', 'tags.name', 'completed']
        )
        for task in tasks:
            if has_filtering_tag(task, optin=False) and not task['completed']:
                print(json.dumps(task))
                sections[section_name].append({
                    'gid': task['gid'],
                    'name': task['name'],
                    'public_description': get_public_description(task)
                })

    return sections

"""
optin: {bool} Whether to filter on an opt in or opt out basis.
    If True, only tasks with the 'roadmap_public' tag will be returned
    If False, all tasks, except those with the roadmap_ignore tag will be returned
"""
def has_filtering_tag(task, optin):
    TAG = 'roadmap_public' if optin else 'roadmap_ignore'
    for tag in task['tags']:
        if tag['name'] == TAG:
            return True

def get_public_description(task):
    for field in task['custom_fields']:
        if field['name'] == 'Public Description':
            return field['text_value']


sections = tasks_by_section()
