# Standard library
import logging
import os
import sys

# Third-party
import asana

# To see workspace GID, log into Asana and then view:
# https://app.asana.com/api/1.0/workspaces
ASANA_WORKSPACE_GID = "133733285600979"
# To see project GIDs, log into Asana and then view:
# https://app.asana.com/api/1.0/projects
#
# To see "Community Team Tracking" project section GIDs, log into Asana and
# then view:
# https://app.asana.com/api/1.0/projects/1172465506923657/sections
ASANA_SECTION_GID = "1172465506923661"
LOG = logging.root


def setup_asana_client():
    LOG.info("Setting up Asana client...")
    try:
        asana_token = os.environ["ADMIN_ASANA_TOKEN"]
    except KeyError:
        LOG.critical("missin ADMIN_ASANA_TOKEN environment variable")
        sys.exit(1)
    asana_client = asana.Client.access_token(asana_token)
    asana_client.headers = {"asana-enable": "new_goal_memberships"}
    try:
        # Perform simple API operation to test authentication
        asana_client.workspaces.get_workspace(ASANA_WORKSPACE_GID)
    except asana.error.NoAuthorizationError as e:
        LOG.critical(f"{e.status} {e.message} (is ADMIN_ASANA_TOKEN valid?)")
        sys.exit(1)
    LOG.success("done.")
    return asana_client


def get_asana_team_members(asana_client):
    LOG.info("Get Team Members...")
    team_members = asana_client.tasks.find_by_section(
        ASANA_SECTION_GID, opt_fields=["name", "custom_fields"]
    )
    LOG.success("done.")
    return team_members
