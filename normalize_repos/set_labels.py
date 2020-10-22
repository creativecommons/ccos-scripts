# Standard library
import logging

# Local/library specific
import log


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

    logger.log(logging.INFO, "Fetching initial labels...")
    initial_labels = {
        label.name.casefold(): label for label in repo.get_labels()
    }
    logger.log(log.SUCCESS, f"done. Found {len(initial_labels)} labels.")

    logger.log(logging.INFO, "Parsing final labels...")
    final_labels = {
        label.qualified_name.casefold(): label for label in final_labels
    }
    logger.log(log.SUCCESS, f"done. Found {len(final_labels)} labels.")

    if not non_destructive:
        logger.log(logging.INFO, f"Syncing initial labels...")
        log.change_indent(+1)
        for initial_label_name, initial_label in initial_labels.items():
            logger.log(logging.INFO, f"Syncing '{initial_label_name}'...")
            log.change_indent(+1)
            if initial_label_name not in final_labels:
                logger.log(logging.INFO, "Does not exist, deleting...")
                initial_label.delete()
                logger.log(log.SUCCESS, "done.")
            log.change_indent(-1)
            logger.log(log.SUCCESS, "done.")
        log.change_indent(-1)
        logger.log(log.SUCCESS, "done.")

    logger.log(logging.INFO, f"Syncing final labels...")
    log.change_indent(+1)
    for final_label_name, final_label in final_labels.items():
        logger.log(logging.INFO, f"Syncing '{final_label_name}'...")
        log.change_indent(+1)
        if final_label_name not in initial_labels:
            logger.log(logging.INFO, "Did not exist, creating...")
            repo.create_label(**final_label.api_arguments)
            logger.log(log.SUCCESS, "done.")
        elif final_label != initial_labels[final_label_name]:
            logger.log(logging.INFO, "Differences found, updating...")
            initial_label = initial_labels[final_label_name]
            initial_label.edit(**final_label.api_arguments)
            logger.log(log.SUCCESS, "done.")
        else:
            logger.log(logging.INFO, "Match found, moving on.")
        log.change_indent(-1)
        logger.log(log.SUCCESS, "done.")
    log.change_indent(-1)
    logger.log(log.SUCCESS, "done.")


def set_labels(repos, standard_labels, repo_specific_labels):
    """
    Set labels on all repos for the organisation. This is the main entrypoint of
    the module.
    """

    for repo in list(repos):
        logger.log(logging.INFO, f"Getting labels for repo '{repo.name}'...")
        labels = standard_labels + repo_specific_labels.get(repo.name, [])
        logger.log(log.SUCCESS, f"done. Found {len(labels)} labels.")
        logger.log(logging.INFO, f"Syncing labels for repo '{repo.name}'...")
        map_repo_to_labels(repo, labels)
        logger.log(log.SUCCESS, "done.")


__all__ = [set_labels]
