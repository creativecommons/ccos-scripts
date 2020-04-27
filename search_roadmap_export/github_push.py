from config import CONFIG

def get_templates(GITHUB_CLIENT):
    oss_repo = GITHUB_CLIENT.get_repo("creativecommons/creativecommons.github.io-source")
    """templates = {
        "page": oss_repo.get_contents("content/contributing-code/cc-search/roadmap-test/page-template.lr"),
        "quarter": oss_repo.get_contents("content/contributing-code/cc-search/roadmap-test/quarter-template.lr"),
        "task": oss_repo.get_contents("content/contributing-code/cc-search/roadmap-test/task-template.lr")
    }"""

    return {
        "page": """_model: page
---
_template: page-with-toc.html
---
title: CC Search Roadmap
---
body:

{{quarters}}""",
        "quarter": """## {{quarter.name}}

<table class="table table-sm table-striped">
    <thead class="thead-light">
        <tr>
            <th scope="col">Task Name</th>
            <th scope="col">Task Description</th>
        </tr>
    </thead>
    <tbody>
        {{quarter.tasks}}
    </tbody>
</table>""",
        "task": """<tr>
    <td>{{task.name}}</td>
    <td>{{task.description}}</td>
</tr>"""
    }

def push_to_repo(GITHUB_CLIENT, content):
    oss_repo = GITHUB_CLIENT.get_repo("creativecommons/creativecommons.github.io-source")
    update = oss_repo.update_file(
        path="content/contributing-code/cc-search/roadmap-test/contents.lr",
        message="Update Search Roadmap",
        content=content,
        sha=CONFIG["GITHUB_ROADMAP_FILE_SHA"],
        branch="add_search-roadmap"
    )
    return update
