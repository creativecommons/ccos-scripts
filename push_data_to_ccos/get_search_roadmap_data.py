"""
This script pulls selected tasks from the CC Search Roadmap Asana project, then
fills that information into a lektor databag, and pushes it to a file in
creativecommons/creativecommons.github.io-source.
"""

# Standard Library
import logging
import os
import re

# Third-party
import asana

from normalize_repos import log

ASANA_ROADMAP_PROJECT_GID = "1140559033201049"
ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
log.set_up_logging()
logger = logging.getLogger("push_data_to_ccos")
log.reset_handler()


def fetch_quarters():
    """
    This method fetches all sections in the roadmap project, then
    using some regex magic, filters out all sections that are not
    named like quarter names. For example:

    Q1 2020
    q1 2021
    q3 2020

    are all matches.
    """
    sections = ASANA_CLIENT.sections.find_by_project(ASANA_ROADMAP_PROJECT_GID)
    for section in sections:
        if re.match(r"Q\d{1}\s\d{4}", section["name"], re.IGNORECASE):
            yield {"name": section["name"], "gid": section["gid"]}


def generate_databag():
    """
    databag schema
    {
        "quarters": [
            {
                "name": "Q1 2020",
                "tasks": [
                    {
                        "gid": "",
                        "name": "",
                        "description": ""
                    },
                    ...
                ]
            },
            {
                "name": "Q2 2020",
                "tasks": []
            },
            ...
        ]
    }

    """
    logger.log(logging.INFO, "Pulling from Asana...")
    databag = {"quarters": []}
    logger.log(logging.INFO, "Generating Databag...")
    for quarter in fetch_quarters():
        logger.log(logging.INFO, "Pulling tasks for quarter - {}...".format(quarter["name"]))
        tasks = ASANA_CLIENT.tasks.find_by_section(  # Get tasks in section
            quarter["gid"],
            opt_fields=["name", "custom_fields", "tags.name", "completed"],
        )
        logger.log(logging.INFO, "Done.")
        quarter = {"name": quarter["name"], "tasks": []}

        logger.log(logging.INFO, "Processing tasks...")
        for task in tasks:
            # if task does not have opt out flag, and is not complete
            if has_filtering_tag(task) and not task["completed"]:
                quarter["tasks"].append(
                    {
                        "gid": task["gid"],
                        "name": task["name"],
                        "description": get_public_description(task),
                    }
                )
        logger.log(logging.INFO, "Done.")
        databag["quarters"].append(quarter)
    logger.log(logging.INFO, "Pruning quarters...")  # remove quarter if it has no tasks
    databag["quarters"] = [
        quarter
        for quarter in databag["quarters"]
        if len(quarter["tasks"]) != 0
    ]
    logger.log(log.SUCCESS, "Pull successful.")

    return databag


def has_filtering_tag(task):
    """
    Indicates if an Asana task has the opt-out tag
    """
    for tag in task["tags"]:
        if tag["name"] == "roadmap_ignore":
            return False
        return True


def get_public_description(task):
    """
    Gets the Public Description field of an Asana Task
    """
    for field in task["custom_fields"]:
        if field["name"] == "Public Description":
            return field["text_value"]


def get_search_roadmap_data():
    data = generate_databag()
    return data
