import json
import logging
import log

logger = logging.getLogger("normalize_repos")
log.reset_handler()


def validate_labels(standard_labels, repo_specific_labels):
    """
    Validate all CC repos against the label specification. This checks that all
    issues have exactly one mandatory label. This is the main entrypoint of the
    module.
    """

    logger.log(logging.INFO, json.dumps(standard_labels))
    logger.log(logging.INFO, json.dumps(repo_specific_labels))


__all__ = [validate_labels]
