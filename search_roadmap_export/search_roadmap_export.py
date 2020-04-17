# Standard Library
import os

# Third-party
import asana
from github import Github

from config import CONFIG

ASANA_CLIENT = asana.Client.access_token(os.environ["ASANA_TOKEN"])

"""
def get_cc_asana_workspace():
    for workspace in ASANA_CLIENT.workspaces.find_all():
        if workspace['name'] == 'creativecommons.org':
            return workspace

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
def tasks_by_section():
    for section_name, section_gid in CONFIG['ROADMAP_SECTIONS'].items():
        tasks = ASANA_CLIENT.tasks.find_by_section(CONFIG['ROADMAP_SECTIONS'][section_name])


"""

"""
def tasks_with_tag():
    return list(map(
        lambda task: task['gid'],
        ASANA_CLIENT.tags.get_tasks_with_tag(CONFIG['ROADMAP_PUBLIC_TAG_GID'])
    ))


def filter_tasks_without_tag(all_in_sections, all_with_tag):
    pass



tasks = ASANA_CLIENT.tags.get_tasks_with_tag(CONFIG['ROADMAP_PUBLIC_TAG_GID'])
for task in tasks:
    print(task)

sections = ASANA_CLIENT.sections.find_by_project(CONFIG['ROADMAP_PROJECT_GID'])
for section in sections:
    print(section)
