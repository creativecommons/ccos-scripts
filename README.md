# Creative Commons (CC) Open Source Scripts

These are scripts used to maintain various pieces of CC's open source community
infrastructure.

## Who is this repository for?

This repository contains internal automation scripts used by the
Creative Commons team to manage their GitHub organization.

It is not intended for general users or beginners to run locally.
Most scripts are executed automatically via GitHub Actions and
require organization-level permissions and access tokens.

If you are new to this repository, you do not need to understand
all workflows or scripts to contribute. Documentation improvements,
clarifications, and small fixes are welcome.



## Status

- [![Sync Community Teams with GitHub][teams_badge]][teams_link]
- [![Manage issues and pull requests in projects][issues_badge]][issues_link]
- [![Normalize Repos][norm_badge]][norm_link]
- [![Push data to CC Open Source][data_badge]][data_link]
- [![Enable workflows][enable_badge]][enable_link]

[teams_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/sync_community_teams.yml/badge.svg
[teams_link]: #sync-community-teams-with-github
[issues_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/manage_issues.yml/badge.svg
[issues_link]: #manage-issues-and-pull-requests-in-projects
[norm_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/normalize_repos.yml/badge.svg
[norm_link]: #normalize-repos
[data_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/push_data_to_ccos.yml/badge.svg
[data_link]: #push-data-to-cc-open-source
[enable_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/enable_workflows.yml/badge.svg
[enable_link]: #enable-workflows


## Code of conduct

[`CODE_OF_CONDUCT.md`][org-coc]:
> The Creative Commons team is committed to fostering a welcoming community.
> This project and all other Creative Commons open source projects are governed
> by our [Code of Conduct][code_of_conduct]. Please report unacceptable
> behavior to [conduct@creativecommons.org](mailto:conduct@creativecommons.org)
> per our [reporting guidelines][reporting_guide].

[org-coc]: https://github.com/creativecommons/.github/blob/main/CODE_OF_CONDUCT.md
[code_of_conduct]: https://opensource.creativecommons.org/community/code-of-conduct/
[reporting_guide]: https://opensource.creativecommons.org/community/code-of-conduct/enforcement/


## Contributing

See [`CONTRIBUTING.md`][org-contrib].

[org-contrib]: https://github.com/creativecommons/.github/blob/main/CONTRIBUTING.md


## Workflows

The following workflows are ordered by schedule frequency and start time.


### Sync Community Teams with GitHub

| **Workflow** | | |
| -- | --: | --- |
| | Schedule: | Hourly at 30 minutes past the hour (`**:30`) |
| | YAML: | [`sync_community_teams.yml`][sync_teams_yml]  |
| **Script** | | |
| | File: | [`sync_community_teams.py`][teams_file] |
| | Common Modules: | [`ccos/`](ccos/) |
| | Specific Modules: | [`ccos/norm/`](ccos/norm/) |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This creates GitHub teams for the Community teams and updates their membership
based on the [`community_team_members.json`][databag] Lektor databag.
- The databag is used to:
  - create the [Community Team Members — Creative Commons Open
    Source][ctlistpage] page
  - configure GitHub team memberships and repository permissions
- The databag is kept up-to-date by [Push data to CC Open
  Source](#push-data-to-cc-open-source), below

[sync_teams_yml]: .github/workflows/sync_community_teams.yml
[teams_file]: sync_community_teams.py
[databag]: https://github.com/creativecommons/ccos-website-source/blob/master/databags/community_team_members.json
[ctlistpage]: https://opensource.creativecommons.org/community/community-team/members/


### Manage new issues and pull requests in projects

| **Workflow** | | |
| -- | --: | --- |
| | Schedule: | Hourly at 45 minutes past the hour (`**:45`) |
| | YAML: | [`manage_issues.yml`][manage_issues] |
| **Script** | | |
| | File: | [`manage_new_issues_and_pull_requests.py`][manage_new_issues] |
| | Common Modules: | [`ccos/`](ccos/) |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This manages new issues and pull requests to ensure they are properly tracked
in a GitHub project:
- [possumbilities project][proj_possumbilities]: _Web Development and Web
  Support_
- [TimidRobot project][proj_timidrobot]: _Application Programming, IT Support,
  Management, Platforms, and Systems_

[manage_issues]: .github/workflows/manage_issues.yml
[manage_new_issues]: manage_new_issues_and_pull_requests.py
[proj_possumbilities]: https://github.com/orgs/creativecommons/projects/23/views/1
[proj-shafiya-heena]: https://github.com/orgs/creativecommons/projects/22/views/1
[proj_timidrobot]: https://github.com/orgs/creativecommons/projects/15/views/1


###  Normalize Repos

| **Workflow** | | |
| -- | --: | --- |
| | Schedule: | Hourly at 45 minutes past the hour (`**:45`) |
| | YAML: | [`normalize_repos.yml`][norm_pr_yml] |
| **Script** | | |
| | File: | [`normalize_repos.py`][norm_file] |
| | Common Modules: | [`ccos/`](ccos/) |
| | Specific Modules: | [`ccos/norm/`](ccos/norm/) |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This ensures that all active repositories in the creativecommons
GitHub organization are consistent in the following ways:
- They have all the labels defined in `labels.yml` present.
- They have standard branch protections set up (with some exceptions).

This will only update color and description of existing labels or create
new labels. It will never delete labels.

[norm_pr_yml]: .github/workflows/normalize_repos.yml
[norm_file]: normalize_repos.py


### Push data to CC Open Source

| **Workflow** | | |
| -- | --: | --- |
| | Schedule: | Daily at midnight:15 (`00:15`) |
| | YAML: | [`push_data_to_ccos.yml`][push_ccos_yml] |
| **Script** | | |
| | File: | [`push_data_to_ccos.py`][data_file] |
| | Common Modules: | [`ccos/`](ccos/) |
| | Specific Modules: | [`ccos/data/`](ccos/data/) |
| **Env** | | |
| | Required: | `ADMIN_ASANA_TOKEN` |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This retreives data from Asana, formats it as a lektor databag, and pushes it
to CC Open Source website source repository:
- Data Source: [Community Team Tracking - Asana][asana] (limited access)
- Data Destination:
  - [`creativecommons/ccos-website-source`][ccos_source]
    - [`databags/community_team_members.json`][db_community]
    - [`databags/repos.json`][db_repos]

The destination data is used by the following pages:
- [Community Team Members — Creative Commons Open Source][ctlistpage]
- [Open Source Projects — Creative Commons Open Source][osproj]

[push_ccos_yml]: .github/workflows/push_data_to_ccos.yml
[data_file]: push_data_to_ccos.py
[ctlistpage]: https://opensource.creativecommons.org/community/community-team/members/
[osproj]: https://opensource.creativecommons.org/contributing-code/projects/
[asana]: https://app.asana.com/0/1172465506923657/list
[ccos_source]: https://github.com/creativecommons/ccos-website-source
[db_community]: https://github.com/creativecommons/ccos-website-source/blob/main/databags/community_team_members.json
[db_repos]: https://github.com/creativecommons/ccos-website-source/blob/main/databags/repos.json


### Eanble Workflows

| **Workflow** | | |
| -- | --: | --- |
| | Schedule: | Monthly on the 1st at 22:22 |
| | YAML: | [`enable_workflows.yml`][enable_workflows_yml] |
| **Script** | | |
| | File: | [`enable_workflows.py`][enable_workflows_file] |
| | Common Modules: | [`ccos/`](ccos/) |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

Enable GitHub Action workflows for specified repositories (ensures that they
are not disabled due to inactivity).

For more information, see [Prevent scheduled GitHub Actions from becoming disabled - Stack Overflow][prevent_scheduled].

[enable_workflows_yml]: .github/workflows/enable_workflows.yml
[enable_workflows_file]: enable_workflows.py
[prevent_scheduled]: https://stackoverflow.com/questions/67184368/prevent-scheduled-github-actions-from-becoming-disabled


## Environment Variables

- `ADMIN_ASANA_TOKEN`: Asana token with access to the Creative Commons Asana
  organization
- `ADMIN_GITHUB_TOKEN`: GitHub token with admin permissions to the
  `creativecommons` GitHub organization


## :robot: Automation Authorship

Scripts that commit code or automatically reply to pull requests and issues
need to be associated with a GitHub user account. Creative Commons maintains a
[cc-open-source-bot](https://github.com/cc-open-source-bot) user for this
purpose. This is useful for a few reasons:

- It's ethically important that our community members know when they are
  talking to a bot instead of a human.
- It makes it easy to audit our automations in the future, because all commits
  and messages will be associated with the single @cc-open-source-bot user
  account via the GitHub search, api, etc.
- We won't need to  update automations when there are changes to staff or
  volunteers.

Using this bot clearly communicates when a commit, comment, or action was
performed by an automation. For example, here is some configuration for a
workflow using the [Add & Commit](https://github.com/EndBug/add-and-commit)
GitHub Action:

```yml
# ...other settings here
- name: Commit changes
  uses: EndBug/add-and-commit@v4
  with:
    author_name: cc-open-source-bot
    author_email: opensource@creativecommons.org
    message: "Deploy site"
    add: "./example-directory"
```


## Development

Local development and testing is facilitated by helper scripts:
- `./dev/tools.sh`: Checks and updates Python formatting
- `.dev/test.sh`: Uses act and Docker to test workflows
  - [nektos/act](https://github.com/nektos/act): _Run your GitHub Actions
    locally 🚀_


### Python Dependencies

- [Asana/python-asana][python-asana]: _Official Python client library for the
  Asana API v1_
- [carpedm20/emoji][emoji]: _e_moji terminal output for Python_
- [gitpython-developers/GitPython][gitpython]: _GitPython is a python library
  used to interact with Git repositories._
- [graphql-python/gql][pygql]: _A GraphQL client in Python_
- [PyGithub/PyGithub][pygithub]: _Typed interactions with the GitHub API v3_
- [PyYAML][pyyaml]: _a full-featured YAML framework for the Python
  programming language_
- [Requests][requests]: _HTTP for Humans™_

[python-asana]: https://github.com/asana/python-asana
[emoji]: https://github.com/carpedm20/emoji/
[gitpython]: https://github.com/gitpython-developers/GitPython
[pygql]: https://github.com/graphql-python/gql
[pygithub]: https://github.com/pygithub/pygithub
[pyyaml]: https://pyyaml.org/
[requests]: https://requests.readthedocs.io/en/latest/


### GitHub GraphQL API

- [Using the API to manage Projects - GitHub Docs][projectsv2api]
- [Forming calls with GraphQL - GitHub Docs][formingcalls]

[projectsv2api]: https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects
[formingcalls]: https://docs.github.com/en/graphql/guides/forming-calls-with-graphql


## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"


### GitHub GraphQL API schema

The GitHub GraphQL API public schema
([`ccos/schema.docs.graphql`][graphqlschema]) was downloaded from [Public
schema - GitHub Docs][publicschema] and is not within scope of the Expat/MIT
license of this project.

[graphqlschema]: ccos/schema.docs.graphql
[publicschema]: https://docs.github.com/en/graphql/overview/public-schema
