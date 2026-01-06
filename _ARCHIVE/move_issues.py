#!/usr/bin/env python3
"""
Ensure all open issues and pull requests are tracked in an appropriate project
and and status column.
"""

# Standard library
import argparse
import sys
import textwrap
import traceback

# Third-party
import yaml
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonTracebackLexer

# First-party/Local
import ccos.log
from ccos import gh_utils

LOG = ccos.log.setup_logger()
PROJECTS_YAML = "ccos/manage/projects.yml"


def setup():
    """Instantiate and configure argparse and logging.

    Return argsparse namespace.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "-c",
        "--count",
        default=None,
        type=int,
        help="only update specified number of issues and pull requests (COUNT"
        " of 3 may result in 6 updates)",
    )
    ap.add_argument(
        "-n",
        "--dryrun",
        action="store_true",
        help="dry run: do not make any changes",
    )
    args = ap.parse_args()
    return args


def read_project_data():
    LOG.info("Reading project data YAML file")
    with open(PROJECTS_YAML, "r") as file_obj:
        project_data = yaml.safe_load(file_obj)
    return project_data


def update_project_data(github_gql_client, project_data):
    LOG.info("Updating project data from GitHub GraphQL API")
    query = gh_utils.gql_query(
        """
        query {
            organization(login:"creativecommons") {
                projectsV2(first: 100) {
                    edges {
                        node {
                            id
                            number
                            title
                            field(name: "Status") {
                                __typename
                                ... on ProjectV2SingleSelectField {
                                    id
                                    name
                                    opt_triage: options(names: "Triage") {
                                        id
                                    }
                                    opt_backlog: options(
                                        names: "Backlog"
                                    ) {
                                        id
                                    }
                                    opt_in_review: options(
                                        names: "In review"
                                    ) {
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
    )
    result = github_gql_client.execute(query)
    for edge in result["organization"]["projectsV2"]["edges"]:
        node = edge["node"]
        title = node["title"]
        field = node["field"]
        if title in project_data.keys():
            project = project_data[title]
            project["id"] = node["id"]
            project["number"] = node["number"]
            project["status_field_id"] = field["id"]
            project["status_triage_id"] = field["opt_triage"][0]["id"]
            project["status_backlog_id"] = field["opt_backlog"][0]["id"]
            project["status_in_review_id"] = field["opt_in_review"][0]["id"]
    return project_data


def get_shafiya_items(github_gql_client):
    LOG.info("Searching for issues and/or pull requests in Shafiya project")
    # https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests
    search_query = (
        "org:creativecommons"
        " state:open"
        " project:creativecommons/22"  # Shafiya-Heena project
    )
    cursor = ""
    edges = []
    next_page = True
    while next_page is True:
        query = gh_utils.gql_query(
            """
            query($cursor: String, $search_query: String!) {
                search(
                    after: $cursor
                    first: 100
                    query: $search_query
                    type: ISSUE
                ) {
                    edges {
                        node {
                            __typename
                            ... on Issue {
                                createdAt
                                id
                                labels(first: 100) {
                                    edges {
                                        node {
                                            name
                                        }
                                    }
                                }
                                number
                                repository {
                                    name
                                }
                            }
                            ... on PullRequest {
                                createdAt
                                id
                                number
                                repository {
                                    name
                                }
                            }
                        }
                    }
                    pageInfo{
                        endCursor
                        hasNextPage
                    }
                }
            }
            """
        )
        params = {"cursor": cursor, "search_query": search_query}
        result = github_gql_client.execute(query, variable_values=params)
        edges += result["search"]["edges"]
        cursor = result["search"]["pageInfo"]["endCursor"]
        next_page = result["search"]["pageInfo"]["hasNextPage"]

    items = {"issues": [], "prs": []}
    for edge in edges:
        node = edge["node"]
        created = node["createdAt"]
        item_id = node["id"]
        number = node["number"]
        repo = node["repository"]["name"]
        type_ = node["__typename"]
        if type_ == "Issue":
            labels = []
            for label_edge in node["labels"]["edges"]:
                labels.append(label_edge["node"]["name"])
            items["issues"].append(
                [repo, number, created, item_id]
            )
        elif type_ == "PullRequest":
            items["prs"].append([repo, number, created, item_id])
    items["issues"].sort()
    items["prs"].sort()
    LOG.info(
        f"Found {len(items['issues']) + len(items['prs'])} open and untracked"
        f" items: {len(items['issues'])} issues, {len(items['prs'])} pull"
        " requests"
    )
    return items


def track_items(args, github_gql_client, project_data, items):
    if args.dryrun:
        noop = "dryrun (no-op): "
    else:
        noop = ""

    query_add_item_to_project = gh_utils.gql(
        """
        mutation($project_id: ID!, $item_id: ID!) {
            addProjectV2ItemById(
                input: {
                    projectId: $project_id
                    contentId: $item_id
                }
            ) {
                item {
                    id
                }
            }
        }
        """
    )
    query_set_status_option = gh_utils.gql(
        """
        mutation(
            $field_id: ID!
            $item_id: ID!
            $project_id: ID!
            $option_id: String
        ) {
            updateProjectV2ItemFieldValue(
                input: {
                    fieldId: $field_id
                    itemId: $item_id
                    projectId: $project_id
                    value: {
                        singleSelectOptionId: $option_id
                    }
                }
            ) {
                projectV2Item {
                    id
                }
            }
        }
        """
    )

    # Add issues to projects
    if args.count is None:
        count = len(items["issues"])
    else:
        count = min(args.count, len(items["issues"]))
    LOG.info(f"{noop}Adding {count} item(s) to projects")
    for item in items["issues"][0 : args.count]:  # noqa: E203
        repo, number, _, item_id = item
        # identify appropriate project
        project_id = None
        field_id = None
        for project in project_data.keys():
            if repo in project_data[project]["repos"]:
                project_id = project_data[project]["id"]
                field_id = project_data[project]["status_field_id"]
                break
        if not project_id:
            LOG.error(f"missing project assignment for repository: {repo}")
            sys.exit(1)
        # add issue to project
        if not args.dryrun:
            params = {"project_id": project_id, "item_id": item_id}
            result = github_gql_client.execute(
                query_add_item_to_project, variable_values=params
            )
            item_id = result["addProjectV2ItemById"]["item"]["id"]
            LOG.change_indent(+1)
            LOG.info(f"{repo}#{number} added to {project} project")
        # move issue to Status: Backlog
        if not args.dryrun:
            option_id = project_data[project]["status_backlog_id"]
            status = "Backlog"
            params = {
                "field_id": field_id,
                "item_id": item_id,
                "project_id": project_id,
                "option_id": option_id,
            }
            result = github_gql_client.execute(
                query_set_status_option, variable_values=params
            )
            ditto = len(f"{repo}#{number}") * "^"
            # 90 is bright black (gray)
            LOG.info(f"\u001b[90m{ditto}\u001b[0m moved to Status: {status}")
        LOG.change_indent(-1)

    # Add pull requests to projects
    if args.count is None:
        count = len(items["prs"])
    else:
        count = min(args.count, len(items["prs"]))
    LOG.info(
        f"{noop}Adding {count} open and untracked pull requests to projects"
    )
    for item in items["prs"][0 : args.count]:  # noqa: E203
        repo, number, _, item_id = item
        # identify appropriate project
        project_id = None
        field_id = None
        for project in project_data.keys():
            if repo in project_data[project]["repos"]:
                project_id = project_data[project]["id"]
                field_id = project_data[project]["status_field_id"]
                break
        if not project_id:
            LOG.error(f"missing project assignment for repository: {repo}")
            sys.exit(1)
        # add pull request to project
        if not args.dryrun:
            params = {"project_id": project_id, "item_id": item_id}
            result = github_gql_client.execute(
                query_add_item_to_project, variable_values=params
            )
            item_id = result["addProjectV2ItemById"]["item"]["id"]
            LOG.change_indent(+1)
            LOG.info(f"{repo}#{number} added to {project} project")
        # move pull request to Status: In review
        if not args.dryrun:
            option_id = project_data[project]["status_in_review_id"]
            params = {
                "field_id": field_id,
                "item_id": item_id,
                "project_id": project_id,
                "option_id": option_id,
            }
            result = github_gql_client.execute(
                query_set_status_option, variable_values=params
            )
            ditto = len(f"{repo}#{number}") * "^"
            # 90 is bright black (gray)
            LOG.info(f"\u001b[90m{ditto}\u001b[0m moved to Status: In review")
        LOG.change_indent(-1)


def main():
    args = setup()

    github_gql_client = gh_utils.setup_github_gql_client()

    project_data = read_project_data()
    project_data = update_project_data(github_gql_client, project_data)

    items = get_shafiya_items(github_gql_client)

    track_items(args, github_gql_client, project_data, items)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOG.info("Halted via KeyboardInterrupt.")
        sys.exit(130)
    except SystemExit as e:
        sys.exit(e.code)
    # Last
    except Exception:
        traceback_formatted = textwrap.indent(
            highlight(
                traceback.format_exc(),
                PythonTracebackLexer(),
                TerminalFormatter(),
            ),
            "    ",
        )
        LOG.critical(f"Unhandled exception:\n{traceback_formatted}")
        sys.exit(1)
