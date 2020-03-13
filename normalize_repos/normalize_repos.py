#!/usr/bin/env python3
# vim: set fileencoding=utf-8:
"""
This script ensures that all active repositories in the creativecommons GitHub
organization are consistent. Please see README.md.
"""
# Standard library
import os

# Third-party
from github import Github

# Local/library specific
from labels import REQUIRED_LABELS


BRANCH_PROTECTION_EXEMPT_REPOSITORIES = [
    # non-engineering repo
    "australian-chapter",
    # non-engineering repo
    "cc-cert-core",
    # non-engineering repo
    "cc-cert-edu",
    # non-engineering repo
    "cc-cert-gov",
    # non-engineering repo
    "cc-cert-lib",
    # exempted to allow transifex updates
    "cc.i18n",
    # exempted to allow community maintainer to self-merge PRs
    "ccsearch-browser-extension",
    # exempted for bot pushes to master
    "creativecommons.github.io-source",
    # exempted for bot pushes to master
    "creativecommons.github.io",
    # non-engineering repo
    "global-network-strategy",
    # non-engineering repo
    "network-platforms",
    # non-engineering repo
    "sre-wiki-js",
    # non-engineering repo
    "tech-support",
]

BRANCH_PROTECTION_REQUIRED_STATUS_CHECK_MAP = {
    "cccatalog-api": ["continuous-integration/travis-ci"],
    "cccatalog-frontend": ["ci/circleci: lint", "ci/circleci: unit"],
    "creativecommons.github.io-source": ["continuous-integration/travis-ci"],
    "fonts": [
        "ci/circleci: lint",
        "ci/circleci: build",
        "netlify/cc-fonts/deploy-preview",
    ],
    "vocabulary": [
        "ci/circleci: lint",
        "ci/circleci: build",
        "netlify/cc-vocabulary/deploy-preview",
    ],
    "vue-vocabulary": [
        "ci/circleci: lint",
        "ci/circleci: unit",
        "netlify/cc-vue-vocabulary/deploy-preview",
    ],
}


def set_up_github_client():
    ADMIN_GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]
    github = Github(ADMIN_GITHUB_TOKEN)
    return github


def get_cc_repos(github):
    cc = github.get_organization("creativecommons")
    return cc.get_repos()


def create_existing_label(labels):
    existing_labels = {}
    for label in labels:
        existing_labels[label.name] = {
            "color": label.color,
            "description": label.description,
            "label_object": label,
        }
    return existing_labels


def edit_label(label_object, name, color, description):
    print(f'Updating color and description for label "{name}"')
    label_object.edit(name=name, color=color, description=description)


def create_label(repo, name, color, description):
    print(f'Creating label "{name}"')
    repo.create_label(name=name, color=color, description=description)


def update_labels(repo):
    if repo.archived:
        return
    print(f"\n{repo.name}\n-----")
    labels = repo.get_labels()
    existing_labels = create_existing_label(labels)
    for label_name in REQUIRED_LABELS.keys():
        required_label = REQUIRED_LABELS[label_name]
        if label_name in existing_labels.keys():
            existing_label = existing_labels[label_name]
            if (required_label["color"] != existing_label["color"]) or (
                required_label["description"] != existing_label["description"]
            ):
                edit_label(
                    label_object=existing_label["label_object"],
                    name=label_name,
                    color=required_label["color"],
                    description=required_label["description"],
                )
        else:
            create_label(
                repo=repo,
                name=label_name,
                color=required_label["color"],
                description=required_label["description"],
            )


def update_branch_protection(repo):
    master = repo.get_branch("master")
    if repo.name not in BRANCH_PROTECTION_EXEMPT_REPOSITORIES:
        if repo.name in BRANCH_PROTECTION_REQUIRED_STATUS_CHECK_MAP:
            master.edit_protection(
                required_approving_review_count=1,
                user_push_restrictions=[],
                strict=True,
                contexts=BRANCH_PROTECTION_REQUIRED_STATUS_CHECK_MAP[
                    repo.name
                ],
            )
        else:
            master.edit_protection(
                required_approving_review_count=1, user_push_restrictions=[]
            )
        print(f'Updating branch protection for: "{repo.name}"')
    else:
        print(f'Skipping branch protection for exempt repo: "{repo.name}"')


if __name__ == "__main__":
    github = set_up_github_client()
    repos = get_cc_repos(github)
    for repo in repos:
        # TODO: Set up automatic deletion of merged branches
        update_labels(repo)
        update_branch_protection(repo)
