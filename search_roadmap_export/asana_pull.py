import json

from config import CONFIG

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
def tasks_by_section(ASANA_CLIENT):
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
            if has_filtering_tag(task) and not task['completed']:
                #print(json.dumps(task))
                sections[section_name].append({
                    'gid': task['gid'],
                    'name': task['name'],
                    'public_description': get_public_description(task)
                })

    return sections

def has_filtering_tag(task):
    for tag in task['tags']:
        if tag['name'] == 'roadmap_ignore':
            return False

        return True

def get_public_description(task):
    for field in task['custom_fields']:
        if field['name'] == 'Public Description':
            return field['text_value']