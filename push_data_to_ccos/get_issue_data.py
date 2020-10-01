from github import Github
import sys
from pathlib import Path

# Locals
sys.path.append((str(Path(__file__).cwd()) + "/utils/"))
from github_utils import get_cc_organization, set_up_github_client


def get_issues(organization):
    ccos_scripts = organization.get_repo("ccos-scripts")
    help_wanted = ccos_scripts.get_label("help wanted")
    return list(
        organization.get_issues(
            filter="all",
            labels=[help_wanted],
        )
    )


def groom_issues(issues):
    return [
        {
            "title": issue.title,
            "labels": [label.name for label in issue.get_labels()],
            "repo": issue.repository.name,
            "url": issue.html_url,
            "number": issue.number,
            "createdAt": int(issue.created_at.timestamp()),
            "updatedAt": int(issue.updated_at.timestamp()),
        }
        for issue in issues
    ]


def get_issue_dict(issues):
    return {"issues": issues}


def get_issue_data():
    github_client = set_up_github_client()
    cc = get_cc_organization(github_client)
    issues = groom_issues(get_issues(cc))
    data = get_issue_dict(issues)
    return data
