# Push Data to CCOS

This folder contains a script that automatically creates GitHub teams and updates their membership based on the Community Team Tracker board on Asana. It uses underlying data from the [Community Team Members page on CC Open Source][ctlistpage] to generate and populate these teams.

[ctlistpage]: httpe://opensource.creativecommons.org/community/community-teams/members/

This script is run via GitHub Actions automatically. 

## Running the Script

1. Install [Pipenv](https://pipenv.readthedocs.io/en/latest/)
2. Navigate to the `sync_community_team` folder and run `pipenv install`
3. Set the `ADMIN_GITHUB_TOKEN` environment variable with your GitHub token. You will need a GitHub token with admin permissions to the `creativecommons` GitHub organization.
5. Run the script: `pipenv run sync_teams.py` (or if you're in a virtual environment already, `python3 sync_teams.py`)

## About the Code

### Community Team Data

Community Team member data is fetched from the Community Team databag hosted on the Creative Commons Open Source website.

### Pushing to GitHub

GitHub teams are created, if non existent, and members are added or removed, as applicable, in the `set_teams_on_github.py` file.


## Repository README

See repository README for licensing information, etc:
- [`../README.md`](../README.md)
