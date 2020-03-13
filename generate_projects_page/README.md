# Generate Projects Page

This script is run via GitHub Actions and generates the [Projects page on CC
Open Source][osproj].

[osproj]:https://opensource.creativecommons.org/contributing-code/projects/


## Running the Script

1. Install [Pipenv](https://pipenv.readthedocs.io/en/latest/)
2. Navigate to the `generate_projects_page` folder and run `pipenv install`
3. Set the `ADMIN_GITHUB_TOKEN` environment variable with your GitHub token.
   You will need a GitHub token with admin permissions to the `creativecommons`
   GitHub organization.
4. Run the script: `python3 normalize_repos.py`


## Repository README

See repository README for licensing information, etc:
- [`../README.md`](../README.md)
