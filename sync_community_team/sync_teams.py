#!/usr/bin/env python3

# Local
from get_community_team_data import get_community_team_data
from set_teams_on_github import create_teams_for_data

if __name__ == "__main__":
    create_teams_for_data(get_community_team_data())
