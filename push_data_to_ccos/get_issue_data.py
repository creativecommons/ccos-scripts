from github import Github

# Locals
from push_data_via_git import GITHUB_ORGANIZATION, GITHUB_TOKEN


def set_up_github_client():
    print("Setting up GitHub client...")
    github_client = Github(GITHUB_TOKEN)
    return github_client


def get_cc_organization(github_client):
    print("Getting CC's GitHub organization...")
    cc = github_client.get_organization(GITHUB_ORGANIZATION)
    return cc


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
        }
        for issue in issues
    ]


def get_issue_dict(issues):
    return {
        "issues": issues
    }


def get_issue_data():
    github_client = set_up_github_client()
    cc = get_cc_organization(github_client)
    issues = groom_issues(get_issues(cc))
    data = get_issue_dict(issues)
    return data
