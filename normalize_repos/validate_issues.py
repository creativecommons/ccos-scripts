# Standard library
import logging
import yaml

# Local/library specific
import log

logger = logging.getLogger("normalize_repos")
log.reset_handler()

TRIAGE_LABEL = "🚦 status: awaiting triage"
LABEL_WORK_REQUIRED_LABEL = "🏷 status: label work required"


def dump_invalid_issues(invalid_issues):
    """
    Dump all invalid issues in a file in the `tmp/` directory.
    @param invalid_issues: the hash of repos and their list of invalid issues
    """

    for invalid_issue_list in invalid_issues.values():
        for invalid_issue in invalid_issue_list:
            issue = invalid_issue['issue']
            invalid_issue['issue'] = issue.title
            invalid_issue['url'] = issue.html_url

    logger.log(logging.INFO, f"Dumping issues in a file...")
    with open('/tmp/invalid_issues.yml', 'w') as file:
        yaml.dump(invalid_issues, file)
    logger.log(log.SUCCESS, "done.")


def are_issue_labels_valid(issue, required_groups):
    """
    Check if the given issue is valid based on the labels applied to it.
    @param issue: the issue whose labels are being validated
    @param required_groups: the label groups which must be applied on all issues
    @return: whether the issues is or isn't valid, and why
    """

    labels = issue.get_labels()
    label_names = {label.name for label in labels}
    if issue.pull_request:
        logger.log(logging.INFO, f"Skipping '{issue.title}' because it is a PR.")
        return True, None  # PRs are exempt
    if TRIAGE_LABEL in label_names:
        logger.log(logging.INFO, f"Skipping '{issue.title}' because it is awaiting triage.")
        return True, None  # Issues that haven't been triaged are exempt

    missing_groups = []
    for group in required_groups:
        required_labels = {
            label.qualified_name
            for label in group.labels
        }
        if not label_names.intersection(required_labels):
            missing_groups.append(group.name)
    if missing_groups:
        issue.add_to_labels(LABEL_WORK_REQUIRED_LABEL)
        logger.log(logging.INFO, f"Issue '{issue.title}' has missing labels.")
        return False, f"Missing labels from groups: {', '.join(missing_groups)}"
    else:
        if LABEL_WORK_REQUIRED_LABEL in label_names:
            issue.remove_from_labels(LABEL_WORK_REQUIRED_LABEL)

    logger.log(logging.INFO, f"Issue '{issue.title}' is OK.")
    return True, None


def get_invalid_issues_in_repo(repo, required_groups):
    """
    Get a list of invalid issues in the given repo with the reason for marking
    them as such.
    @param repo: the repo in which to check for the validity of issues
    @param required_groups: the label groups which must be applied on all issues
    @return: a list of invalid issues and their causes
    """

    logger.log(logging.INFO, f"Getting issues for repo '{repo.name}'...")
    issues = repo.get_issues(state="open")
    logger.log(log.SUCCESS, f"done.")

    invalid_issues = []
    log.change_indent(+1)
    for issue in issues:
        logger.log(logging.INFO, f"Checking labels on '{issue.title}'...")
        are_valid, reason = are_issue_labels_valid(issue, required_groups)
        if not are_valid:
            invalid_issues.append({
                "issue": issue,
                "reason": reason
            })
        logger.log(log.SUCCESS, "done.")
    log.change_indent(-1)
    return invalid_issues


def get_required_groups(groups):
    """
    Get the list of all the groups, at least one label of which is required to
    be present on every triaged issue.
    @param groups: the groups to filter
    @return: the filtered list of groups that that are required by definition
    """

    logger.log(logging.INFO, f"Filtering {len(groups)} groups...")
    required_groups = [group for group in groups if group.is_required]
    logger.log(log.SUCCESS, f"done. Required {len(required_groups)} groups.")
    return required_groups


def validate_issues(repos, groups):
    """
    Validate the labels on all issues in all repos for the organisation. This is
    the main entrypoint of the module.
    """

    required_groups = get_required_groups(groups)
    invalid_issues = {}

    logger.log(logging.INFO, f"Finding issues with invalid labels...")
    log.change_indent(+1)
    for repo in list(repos):
        logger.log(logging.INFO, f"Checking issues in repo '{repo.name}'...")
        invalid_issues[repo.name] = get_invalid_issues_in_repo(repo, required_groups)
        logger.log(log.SUCCESS, f"done.")
    log.change_indent(-1)
    logger.log(log.SUCCESS, f"done.")

    dump_invalid_issues(invalid_issues)


__all__ = [validate_issues]
