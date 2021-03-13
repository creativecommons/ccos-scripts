# Push Data to CCOS

This folder contains a script that pushes the latest version of dynamically generated data to CC Open Source. This data updates the following pages:
* [Community Team Members page on CC Open Source][ctlistpage]
* [Projects page on CC Open Source][osproj].

[ctlistpage]: httpe://opensource.creativecommons.org/community/community-teams/members/
[osproj]: https://opensource.creativecommons.org/contributing-code/projects/

This script is run via GitHub Actions automatically. 

## Running the Script

1. Install [Pipenv](https://pipenv.readthedocs.io/en/latest/)
2. Navigate to the `push_data_to_ccos` folder and run `pipenv install`
3. Set the `ADMIN_GITHUB_TOKEN` environment variable with your GitHub token. You will need a GitHub token with admin permissions to the `creativecommons` GitHub organization.
4. Set the ADMIN_ASANA_TOKEN environment variable with your Asana token. You will need an Asana token with access to the Creative Commons Asana organization.
5. Run the script: `pipenv run sync_data.py` (or if you're in a virtual environment already, `python3 sync_data.py`)

## About the Code

### Repository data

Repository data is generated in `get_repo_data.py` and pulls data on CC repositories using the GitHub API.

### Community Team Data

Community Team member data is generated from the `Community Teams Tracking` Asana project in CC's Asana organization.

### Pushing to GitHub

Data is pushed to the [`creativecommons.github.io-source`](https://github.com/creativecommons/creativecommons.github.io-source) repository via the `push_data_via_git.py` script.


## Repository README

See repository README for licensing information, etc:
- [`../README.md`](../README.md)
