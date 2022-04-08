# Creative Commons (CC) Open Source Scripts

These are scripts used to maintain various pieces of CC's open source community
infrastructure.


## Workflows

The following workflows are ordered by schedule frequency and start time.


### Add Community PRs to Project

| **Workflow** | | |
| -- | --: | --- |
| | Status: | [![Add Community PRs to Project][prs_badge]][prs_link] |
| | Schedule: | Hourly at 5 minutes past the hour (`**:05`) |
| | YAML: | [`add_community_pr.yml`][community_pr_yml] |
| **Action** | | |
| | | [subhamX/github-project-bot][proj_bot] |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This workflow adds community PRs in the
[creativecommons/vocabulary][vocab_repo] repository to [Vocabulary
Planning][vocab_plan] project.

[prs_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/add_community_pr.yml/badge.svg
[prs_link]: https://github.com/creativecommons/ccos-scripts/actions/workflows/add_community_pr.yml
[community_pr_yml]: .github/workflows/add_community_pr.yml
[proj_bot]: https://github.com/subhamX/github-project-bot
[vocab_repo]: https://github.com/creativecommons/vocabulary
[vocab_plan]: https://github.com/orgs/creativecommons/projects/13


### Sync Community Teams with GitHub

| **Workflow** | | |
| -- | --: | --- |
| | Status: | [![Sync Community Teams with GitHub][team_badge]][team_link] |
| | Schedule: | Hourly at 30 minutes past the hour (`**:30`) |
| | YAML: | [`sync_community_team.yml`][sync_team_yml]  |
| **Script** | | |
| | File: | [`sync_community_teams.py`][team_file] |
| | Common Modules: | [`ccos/`](ccos/) |
| | Specific Modules: | [`ccos/norm/`](ccos/norm/) |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This worflow creates GitHub teams for the Community teams and updates their membership based on the [`community_team_members.json`][databag] Lektor databag.
 - The databag is used to create the [Community Team Members — Creative
   Commons Open Source][ctlistpage] page
 - The databag is kept up-to-date by [Push data to CC Open
   Source](#push-data-to-cc-open-source), above

[team_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/sync_community_team.yml/badge.svg
[team_link]: https://github.com/creativecommons/ccos-scripts/actions/workflows/sync_community_team.yml
[team_file]: sync_community_teams.py
[databag]: https://github.com/creativecommons/creativecommons.github.io-source/blob/master/databags/community_team_members.json
[ctlistpage]: https://opensource.creativecommons.org/community/community-team/members/


### Track new issues in backlog

| **Workflow** | | |
| -- | --: | --- |
| | Status: | [![Track new issues in backlog][backlog_badge]][backlog_link] |
| | Schedule: | Hourly at 45 minutes past the hour (`**:45`) |
| | YAML: | [`track_backlog.yml`][track_backlog] |
| **Action** | | |
| | | [dhruvkb/issue-projector][issue_bot] |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This workflow adds PRs to [Active Sprint: Code Review][active_sprint] and new issues to [Backlog: Pending Review][backlog_pending].

[backlog_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/track_backlog.yml/badge.svg
[backlog_link]: https://github.com/creativecommons/ccos-scripts/actions/workflows/track_backlog.yml
[track_backlog]: .github/workflows/track_backlog.yml
[issue_bot]: https://github.com/dhruvkb/issue-projector
[active_sprint]: https://github.com/orgs/creativecommons/projects/7
[backlog_pending]: https://github.com/orgs/creativecommons/projects/10


###  Normalize Repos

| **Workflow** | | |
| -- | --: | --- |
| | Status: | [![Normalize Repos][norm_badge]][norm_link] |
| | Schedule: | Hourly at 45 minutes past the hour (`**:45`) |
| | YAML: | [`normalize_repos.yml`][norm_pr_yml] |
| **Script** | | |
| | File: | [`normalize_repos.py`][norm_file] |
| | Common Modules: | [`ccos/`](ccos/) |
| | Specific Modules: | [`ccos/norm/`](ccos/norm/) |
| **Env** | | |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This workflow ensures that all active repositories in the creativecommons
GitHub organization are consistent in the following ways:
- They have all the labels defined in `labels.yml` present.
- They have standard branch protections set up (with some exceptions).

This script will only update color and description of existing labels or create
new labels. It will never delete labels.

[norm_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/normalize_repos.yml/badge.svg
[norm_link]: https://github.com/creativecommons/ccos-scripts/actions/workflows/normalize_repos.yml
[norm_pr_yml]: .github/workflows/normalize_repos.yml
[norm_file]: normalize_repos.py


### Push data to CC Open Source

| **Workflow** | | |
| -- | --: | --- |
| | Status: | [![Push data to CC Open Source][data_badge]][data_link] |
| | Schedule: | Daily at midnight:15 (`00:15`) |
| | YAML: | [`push_data_to_ccos.yml`][push_ccos_yml] |
| **Script** | | |
| | File: | [`push_data_to_ccos.py`][data_file] |
| | Common Modules: | [`ccos/`](ccos/) |
| | Specific Modules: | [`ccos/data/`](ccos/data/) |
| **Env** | | |
| | Required: | `ADMIN_ASANA_TOKEN` |
| | Required: | `ADMIN_GITHUB_TOKEN` |

This workflow retreives data from Asana, formats it as a lektor databag, and
pushes it to CC Open Source website source repository:
- Data Source: [Community Team Tracking - Asana][asana] (limited access)
- Data Destination:
  - [`creativecommons/creativecommons.github.io-source`][ccos_source]
    - [`databags/community_team_members.json`][db_community]
    - [`databags/repos.json`][db_repos]

The destination data is used by the following pages:
- [Community Team Members — Creative Commons Open Source][ctlistpage]
- [Open Source Projects — Creative Commons Open Source][osproj]

[data_badge]: https://github.com/creativecommons/ccos-scripts/actions/workflows/push_data_to_ccos.yml/badge.svg
[data_link]: https://github.com/creativecommons/ccos-scripts/actions/workflows/push_data_to_ccos.yml
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


## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"
