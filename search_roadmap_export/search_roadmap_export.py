"""
This script pulls selected tasks from the CC Search Roadmap Asana project, then
fills that information into a lektor template, and pushes it to a file in
creativecommons/creativecommons.github.io-source.
"""

# Standard Library
import os

# Third-party
import asana
from github import Github

import asana_pull
import github_push

def build_content(templates, asana_data):
    quarters = ""
    for quarter_name, quarter_tasks in asana_data.items():
        quarter_content = templates["quarter"].replace("{{quarter.name}}", quarter_name)
        quarter_tasks_table = ""
        for task in quarter_tasks:
            quarter_tasks_table += templates["task"].replace("{{task.name}}", task["name"]).replace("{{task.description}}", task["public_description"])

        quarters += quarter_content.replace("{{quarter.tasks}}", quarter_tasks_table)

    return templates["page"].replace("{{quarters}}", quarters)


ASANA_CLIENT = asana.Client.access_token(os.environ["ASANA_TOKEN"])
print("Pulling from Asana...")
sections = asana_pull.tasks_by_section(ASANA_CLIENT)
print("Pull successful.")

GITHUB_CLIENT = Github(os.environ["GITHUB_TOKEN_CC"])
print("Pulling GitHub content templates...")
content_templates = github_push.get_templates(GITHUB_CLIENT)
print("Pull successful.")

print("Generating open source page content...")
new_content = build_content(content_templates, sections)
print("Generated.")

with open("test_content.txt", "w") as f:
    f.write(new_content)

print("Pushing page content to open source repo...")
push_data = github_push.push_to_repo(GITHUB_CLIENT, new_content)
print("Pushed successfully. Commit Info: {}".format(push_data))
