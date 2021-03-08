#!/usr/bin/env python3
# vim: set fileencoding=utf-8:

# Standard library
import argparse

# First-party/Local
from get_community_team_data import get_community_team_data
from get_repo_data import get_repo_data
from push_data_via_git import push_data

daily_databags = ["repos", "community_team_members"]
parser = argparse.ArgumentParser(description="Sync data to CCOS")
parser.add_argument(
    "databags",
    action="store",
    nargs="*",
    default=daily_databags,
    help="the list of all databags to sync to CCOS",
)

if __name__ == "__main__":
    args = parser.parse_args()
    databag_source_map = {
        "repos": get_repo_data,
        "community_team_members": get_community_team_data,
    }
    for databag, source in databag_source_map.items():
        if databag in args.databags:
            push_data(source(), f"{databag}.json")
