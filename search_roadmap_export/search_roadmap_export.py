# Standard Library
import os
import json

# Third-party
import asana
from github import Github

from config import CONFIG

ASANA_CLIENT = asana.Client.access_token(os.environ["ASANA_TOKEN"])


def get_cc_asana_workspace():
    for workspace in ASANA_CLIENT.workspaces.find_all():
        if workspace['name'] == 'creativecommons.org':
            return workspace['gid']
"""
def get_search_roadmap_project(workspace):
    for project in ASANA_CLIENT.projects.find_by_workspace(
        workspace['gid'],
        iterator_type=None
    ):
        if project['name'] == 'CC Search Roadmap':
            return project

workspace = get_cc_asana_workspace()
project = get_search_roadmap_project(workspace)
print(project['gid'])
"""

"""
{
    gid: name
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
            opt_fields=['name', 'custom_fields', 'tags.gid']
        )
        for task in tasks:
            if not has_ignore_tag(task):
                print(task)
                sections[section_name].append({
                    'gid': task['gid'],
                    'name': task['name'],
                    'public_description': get_public_description(task)
                })

    return sections

def has_ignore_tag(task):
    for tag in task['tags']:
        return tag['gid'] == CONFIG['ROADMAP_IGNORE_TAG_GID']

def get_public_description(task):
    custfields = task['custom_fields']
    for field in custfields:
        if field['name'] == 'Public Description':
            return field['text_value']

"""
Returns a list of task gids, each for a task tagged with the 'roadmap_public' tag.
"""
def tasks_with_tag():
    return list(map(
        lambda task: task['gid'],
        ASANA_CLIENT.tags.get_tasks_with_tag(CONFIG['ROADMAP_PUBLIC_TAG_GID'])
    ))


def filter_tasks_without_tag(tasks_by_section, tasks_with_tag):
    sections = {
        'Q12020': [],
        'Q22020': [],
        'Q32020': [],
        'Q42020': []
    }

    for section, tasks in tasks_by_section.items():
        for task in tasks:
            if task['gid'] in tasks_with_tag:
                sections[section].append(task)

    return sections


"""
tasks = ASANA_CLIENT.tags.get_tasks_with_tag(CONFIG['ROADMAP_PUBLIC_TAG_GID'])
for task in tasks:
    print(task)

sections = ASANA_CLIENT.sections.find_by_project(CONFIG['ROADMAP_PROJECT_GID'])
for section in sections:
    print(section)


customfields = ASANA_CLIENT.custom_fields.find_by_workspace(
    CONFIG['CC_WORKSPACE_GID']
)
for field in customfields:
    print(field)
"""

sections = tasks_by_section()

print(json.dumps(sections))

"""
for k, v in filtered.items():
    print(k)
    for gid, name in v.items():
        print('\t{}: {}'.format(gid, name))
        """
