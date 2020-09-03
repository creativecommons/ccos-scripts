import logging
import log

from utils import set_up_github_client, get_cc_organization

logger = logging.getLogger("normalize_repos")
log.reset_handler()


def map_repo_to_labels(repo, final_labels, non_destructive=True):
    """
    Map the given list of labels to GitHub. Any labels that do not already exist
    on the repository will be created and if chosen to, any additional lables on
    the repository will be removed.
    @param repo: the repo on which the labels are being synced
    @param final_labels: the list of labels that should be present on the repo
    @param non_destructive: whether to trim extra labels or preserve them
    """

    logger.log(logging.INFO, "Fetching existing labels...")
    existing_labels = list(repo.get_labels())
    logger.log(log.SUCCESS, f"done. Found {len(existing_labels)} labels.")

    existing_label_names = {
        existing_label.name for existing_label in existing_labels
    }
    final_label_names = {label.qualified_name for label in final_labels}

    if not non_destructive:
        labels_to_delete = [
            label
            for label in existing_labels
            if label.name not in final_label_names
        ]
        logger.log(
            logging.WARNING, f"Deleting {len(labels_to_delete)} labels..."
        )
        log.change_indent(+1)
        for label in labels_to_delete:
            logger.log(logging.WARNING, f"Deleting label '{label.name}'...")
            label.delete()
            logger.log(log.SUCCESS, "done.")
        log.change_indent(-1)
        logger.log(log.SUCCESS, "done.")

    labels_to_create = [
        label
        for label in final_labels
        if label.qualified_name not in existing_label_names
    ]
    logger.log(logging.INFO, f"Creating {len(labels_to_create)} labels...")
    log.change_indent(+1)
    for label in labels_to_create:
        logger.log(logging.INFO, f"Creating label '{label.name}'...")
        repo.create_label(**label.api_arguments)
        logger.log(log.SUCCESS, "done.")
    log.change_indent(-1)
    logger.log(log.SUCCESS, "done.")


def set_labels(standard_labels, repo_specific_labels):
    """
    Set labels on all repos for the organisation. This is the main entrypoint of
    the module.
    """

    logger.log(logging.INFO, "Setting up...")
    client = set_up_github_client()
    organization = get_cc_organization(client)
    logger.log(log.SUCCESS, "done.")

    logger.log(logging.INFO, "Fetching repos...")
    repos = list(organization.get_repos())
    logger.log(log.SUCCESS, f"done. Found {len(repos)} repos.")

    for repo in repos:
        logger.log(logging.INFO, f"Getting labels for repo '{repo.name}'...")
        labels = standard_labels + repo_specific_labels.get(repo.name, [])
        logger.log(log.SUCCESS, f"done. Found {len(labels)} labels.")
        logger.log(logging.INFO, f"Syncing labels for repo '{repo.name}'...")
        map_repo_to_labels(repo, labels)
        logger.log(log.SUCCESS, "done.")


__all__ = [set_labels]
