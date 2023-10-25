# Creative Commons (CC) Open Source Scripts

These are scripts used to maintain various pieces of CC's open source community
infrastructure.


## Status

- [![Add Community PRs to Project][prs_badge]][prs_link]
- [![Sync Community Teams with GitHub][teams_badge]][teams_link]
- [![Manage issues and pull requests in projects][issues_badge]][issues_link]
- [![Normalize Repos][norm_badge]][norm_link]
- [![Push data to CC Open Source][data_badge]][data_link]

[prs_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/add_community_pr.yml/badge.svg
[prs_link]: #add-community-prs-to-project
[teams_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/sync_community_teams.yml/badge.svg
[teams_link]: #sync-community-teams-with-github
[issues_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/manage_issues.yml/badge.svg
[issues_link]: #manage-issues-and-pull-requests-in-projects
[norm_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/normalize_repos.yml/badge.svg
[norm_link]: #normalize-repos
[data_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/push_data_to_ccos.yml/badge.svg
[data_link]: #push-data-to-cc-open-source


## Code of Conduct

[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md):
> The Creative Commons team is committed to fostering a welcoming community.
> This project and all other Creative Commons open source projects are governed
> by our [Code of Conduct][code_of_conduct]. Please report unacceptable
> behavior to [conduct@creativecommons.org](mailto:conduct@creativecommons.org)
> per our [reporting guidelines][reporting_guide].

[code_of_conduct]: https://opensource.creativecommons.org/community/code-of-conduct/
[reporting_guide]: https://opensource.creativecommons.org/community/code-of-conduct/enforcement/


## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).


## Workflows

The following workflows are ordered by schedule frequency and start time.


### Add Community PRs to Project

| **Workflow** | | |
| -- | --: | --- |
| | Schedule: | Hourly at 5 minutes past the hour (`**:05`) |
| | YAML: | [`add_community_pr.yml`][community_pr_yml] |
| **Action** | | |
| | | [subhamX/github-project-bot][proj_bot] |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This workflow adds community PRs in the
[creativecommons/vocabulary][vocab_repo] repository to [Vocabulary
Planning][vocab_plan] project.

[community_pr_yml]: .github/workflows/add_community_pr.yml
[proj_bot]: https://github.com/subhamX/github-project-bot
[vocab_repo]: https://github.com/creativecommons/vocabulary
[vocab_plan]: https://github.com/orgs/creativecommons/projects/13


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
[databag]: https://github.com/creativecommons/creativecommons.github.io-source/blob/master/databags/community_team_members.json
[ctlistpage]: https://opensource.creativecommons.org/community/community-team/members/


### Manage issues and pull requests in projects

| **Workflow** | | |
| -- | --: | --- |
| | Schedule: | Hourly at 45 minutes past the hour (`**:45`) |
| | YAML: | [`manage_issues.yml`][manage_issues] |
| **Script** | | |
| | File: | [`move_closed_issues.py`][move_file] |
| | File: | [`track_issues_and_pull_requests.py`][track_issues] |
| | Common Modules: | [`ccos/`](ccos/) |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This manages issues and pull requests to ensure they are properly tracked
within the [Active Sprint][active_sprint] and [Backlog][backlog] projects:
  - Move closed issues from [Backlog][backlog] to [Active
    Sprint][active_sprint]: Done
  - Track open issues in [Backlog][backlog]: Pending Review
  - Track open pull requests in [Active Sprint][active_sprint]: Code Review

[manage_issues]: .github/workflows/manage_issues.yml
[move_file]: move_closed_issues.py
[track_issues]: track_issues_and_pull_requests.py
[active_sprint]: https://github.com/orgs/creativecommons/projects/7
[backlog]: https://github.com/orgs/creativecommons/projects/10


###  Normalize Repos

| **Workflow** | | |
| -- | --: | --- |
| | Schedule: | Hourly at 45 minutes past the hour (`**:45`) |
| | YAML: | [`normalize_repos.yml`][norm_pr_yml] |
| **Script** | | |
| | File: | [`normalize_repos.py`][norm_file] |
| | Common Modules: | [`ccos/`](ccos/) |
| | Specific Modules: | [`ccos/norm/`](ccos/norm/) |
| **Action** | | |
| | | [gautamkrishnar/keepalive-workflow][keepalive] |
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
[keepalive]: https://github.com/gautamkrishnar/keepalive-workflow


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
  - [`creativecommons/creativecommons.github.io-source`][ccos_source]
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
[ccos_source]: https://github.com/creativecommons/creativecommons.github.io-source
[db_community]: https://github.com/creativecommons/creativecommons.github.io-source/blob/main/databags/community_team_members.json
[db_repos]: https://github.com/creativecommons/creativecommons.github.io-source/blob/main/databags/repos.json


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


## Python Dependencies

- [Asana/python-asana][python-asana]: Official Python client library for the
  Asana API v1
- [carpedm20/emoji][emoji]: emoji terminal output for Python
- [gitpython-developers/GitPython][gitpython]: GitPython is a python library
  used to interact with Git repositories.
- [PyGithub/PyGithub][pygithub]: Typed interactions with the GitHub API v3
- [PyYAML][pyyaml] is a full-featured YAML framework for the Python programming
  language
- [Requests][requests]: HTTP for Humans™

[python-asana]: https://github.com/asana/python-asana
[emoji]: https://github.com/carpedm20/emoji/
[gitpython]: https://github.com/gitpython-developers/GitPython
[pygithub]: https://github.com/pygithub/pygithub
[pyyaml]: https://pyyaml.org/
[requests]: https://requests.readthedocs.io/en/latest/


## Local GitHub Action testing

The GitHub Actions can be tested locally using:
- [nektos/act](https://github.com/nektos/act): _Run your GitHub Actions locally
  🚀_

On ARM laptops (ex. M1 MacBook Pros), there may not be docker images available.
You may have to specify the linux/amd64 architecture. For example:
```shell
act --secret ADMIN_GITHUB_TOKEN --container-architecture linux/amd64 --rm \
    --job manage_issues_and_pull_requests
```
(this assumes that the `ADMIN_GITHUB_TOKEN` environment variable has been set)


## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"
