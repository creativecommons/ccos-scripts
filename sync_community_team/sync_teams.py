#!/usr/bin/env python3

# Local
# First-party/Local
from get_community_team_data import get_community_team_data
from set_codeowners import create_codeowners_for_data
from set_teams_on_github import create_teams_for_data

if __name__ == "__main__":
    create_teams_for_data(get_community_team_data())
    create_codeowners_for_data(get_community_team_data())
