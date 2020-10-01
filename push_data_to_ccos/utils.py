# Standard Lib
import os

# Third party
import asana


ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
ASANA_PROJECT_GID = "1172465506923661"
ASANA_ROADMAP_PROJECT_GID = "1140559033201049"


def get_members_asana():
    return ASANA_CLIENT.tasks.find_by_section(
        ASANA_PROJECT_GID, opt_fields=["name", "custom_fields"]
    )


def get_sections_asana():
    return ASANA_CLIENT.sections.find_by_project(ASANA_ROADMAP_PROJECT_GID)


def get_tasks_asana(gid):
    return ASANA_CLIENT.tasks.find_by_section(  # Get tasks in section
        gid,
        opt_fields=["name", "custom_fields", "tags.name", "completed"],
    )
