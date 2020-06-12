#!/usr/bin/env python3
# vim: set fileencoding=utf-8:

# Local
from get_community_team_data import get_community_team_data
from get_repo_data import get_repo_data
from get_search_roadmap_data import get_search_roadmap_data
from push_data_via_git import push_data


if __name__ == "__main__":
    push_data(get_repo_data(), 'repos.json')
    push_data(get_search_roadmap_data(), 'search_roadmap.json')
    push_data(get_community_team_data(), 'community_team_members.json')
