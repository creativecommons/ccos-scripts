# Push Data to CCOS

This folder contains a script (`sync_teams.py`) that automatically:
1. creates GitHub teams
2. updates their membership based on the
   [`community_team_members.json`][databag] databag
   - The databag is used to create the [Community Team Members — Creative
     Commons Open Source][ctlistpage] page
   - The databag is populated from the Community Team Tracker board on Asana by
     [`../push_data_to_ccos/`](../push_data_to_ccos/)

[databag]: https://github.com/creativecommons/creativecommons.github.io-source/blob/master/databags/community_team_members.json
[ctlistpage]: https://opensource.creativecommons.org/community/community-team/members/

This script is run via GitHub Actions automatically.

## Running the Script

1. Install [Pipenv](https://pipenv.readthedocs.io/en/latest/)
2. Navigate to the `sync_community_team` folder and run `pipenv install`
3. Set the `ADMIN_GITHUB_TOKEN` environment variable with your GitHub token.
   You will need a GitHub token with admin permissions to the `creativecommons`
   GitHub organization.
5. Run the script: `pipenv run sync_teams.py` (or if you're in a virtual
   environment already, `python3 sync_teams.py`)

## About the Code

### Community Team Data

Community Team member data is fetched from the Community Team databag hosted on the Creative Commons Open Source website.

### Pushing to GitHub

GitHub teams are created, if non existent, and members are added or removed, as applicable, in the `set_teams_on_github.py` file.


## Repository README

See repository README for licensing information, etc:
- [`../README.md`](../README.md)
