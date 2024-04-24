# Standard library
import logging

# Third-party
import yaml

TRIAGE_LABEL = "🚦 status: awaiting triage"
LABEL_WORK_REQUIRED_LABEL = "🏷 status: label work required"
LOG = logging.root


def dump_invalid_issues(invalid_issues):
    """
    Dump all invalid issues in a file in the `tmp/` directory.
    @param invalid_issues: the hash of repos and their list of invalid issues
    """
    for invalid_issue_list in invalid_issues.values():
        for invalid_issue in invalid_issue_list:
            issue = invalid_issue["issue"]
            invalid_issue["issue"] = issue.title
            invalid_issue["url"] = issue.html_url

    LOG.info("Dumping issues in a file...")
    with open("/tmp/invalid_issues.yml", "w") as file:
        yaml.dump(invalid_issues, file)
    LOG.success("done.")


def are_issue_labels_valid(issue, required_label_groups):
    """
    Check if the given issue is valid based on the labels applied to it.
    @param issue: the issue whose labels are being validated
    @param required_label_groups: the label groups which must be applied on all
        issues
    @return: whether the issues is or isn't valid, and why
    """
    labels = issue.get_labels()
    label_names = {label.name for label in labels}
    if issue.pull_request:
        LOG.log(logging.INFO, f"Skipping '{issue.title}' because it is a PR.")
        return True, None  # PRs are exempt
    if TRIAGE_LABEL in label_names:
        LOG.log(
            logging.INFO,
            f"Skipping '{issue.title}' because it is awaiting triage.",
        )
        return True, None  # Issues that haven't been triaged are exempt

    missing_label_groups = []
    for group in required_label_groups:
        required_labels = {label.qualified_name for label in group.labels}
        if not label_names.intersection(required_labels):
            missing_label_groups.append(group.name)
    if missing_label_groups:
        issue.add_to_labels(LABEL_WORK_REQUIRED_LABEL)
        LOG.info(f"Issue '{issue.title}' has missing labels.")
        return (
            False,
            "Missing labels from label groups:"
            f" {', '.join(missing_label_groups)}",
        )
    else:
        LOG.info(f"Issue '{issue.title}' is OK.")
        return True, None


def get_invalid_issues_in_repo(repo, required_label_groups):
    """
    Get a list of invalid issues in the given repo with the reason for marking
    them as such.
    @param repo: the repo in which to check for the validity of issues
    @param required_label_groups: the label groups which must be applied on all
        issues
    @return: a list of invalid issues and their causes
    """
    LOG.info(f"Getting issues for repo '{repo.name}'...")
    issues = repo.get_issues(state="open")
    LOG.success("done.")

    invalid_issues = []
    LOG.change_indent(+1)
    for issue in issues:
        LOG.info(f"Checking labels on '{issue.title}'...")
        are_valid, reason = are_issue_labels_valid(
            issue, required_label_groups
        )
        if not are_valid:
            invalid_issues.append({"issue": issue, "reason": reason})
        LOG.success("done.")
    LOG.change_indent(-1)
    return invalid_issues


def validate_issues(repos, required_label_groups):
    """
    Validate the labels on all issues in all repos for the organisation. This
    is the main entrypoint of the module.
    """
    LOG.info("Finding issues with invalid labels...")
    invalid_issues = {}
    LOG.change_indent(+1)
    for repo in list(repos):
        if repo.private:
            LOG.info(f"{repo.name}: skipping: repository is private")
        else:
            LOG.info(f"Checking issues in repo '{repo.name}'...")
            invalid_issues[repo.name] = get_invalid_issues_in_repo(
                repo, required_label_groups
            )
            LOG.success("done.")
    LOG.change_indent(-1)
    LOG.success("done.")

    LOG.change_indent(-1)
    dump_invalid_issues(invalid_issues)
    LOG.change_indent(+1)


__all__ = ["validate_issues"]
