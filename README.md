# CC Open Source Scripts

These are scripts used to maintain various pieces of CC's open source community
infrastructure.


## Scripts

Please see the individual README files in the folder for each script for
information about that script.

| Directory Name                      | Script Purpose |
| ----------------------------------- | -------------- |
| [`normalize_repos`][norm]           | Ensures that all CC repos have standard labels and branch protections |
| [`push_data_to_ccos`][push_to_ccos] | Generates various pages with dynamic data on [CC Open Source][ccos] |
| [`sync_community_team`][sync_team]  | Syncs all Community Team memberships with corresponding memberships in GitHub teams |

[norm]: normalize_repos/
[push_to_ccos]: push_data_to_ccos/
[ccos]: httpe://opensource.creativecommons.org/
[sync_team]: sync_community_team/


## Workflows

| Workflow Name/Status | YML File Name | Workflow Purpose |
| -------------------- | ------------- | ---------------- |
| [![Add Community PRs to Project][b1]][l1] | [`add_community_pr.yml`][community_pr_yml] | Runs hourly at 5 minutes past every hour UTC and adds new Vocabulary issues to [Vocabulary: In Progress][vocab_in_progress] |
| [![Normalize Repos][b2]][l2] | [`normalize_repos.yml`][norm_pr_yml] | Runs daily at 00:00 UTC and whenever someone pushes to the main branch and uses [`normalize_repos`][norm] |
| [![Push data to CC Open Source][b3]][l3] | [`push_data_to_ccos.yml`][push_ccos_yml] | Runs daily at 00:00 UTC and whenever someone pushes to the main branch and uses [`push_data_to_ccos`][push_to_ccos] |
| [![Sync Community Teams with GitHub][b4]][l4] | [`sync_community_team.yml`][sync_team_yml] | Runs daily at 00:30 UTC and whenever someone pushes to the main branch and uses [`sync_community_team`][sync_team] |
| [![Track new issues in backlog][b5]][l5] | [`track_backlog.yml`][track_backlog] | Runs hourly at 45 minutes past every hour UTC and adds PRs to [Active Sprint: Code Review][active_sprint] and new issues to [Backlog: Pending Review][backlog_pending]. Uses [dhruvkb/issue-projector][issue-projector]. |


[b1]: https://github.com/creativecommons/ccos-scripts/actions/workflows/add_community_pr.yml/badge.svg
[l1]: https://github.com/creativecommons/ccos-scripts/actions/workflows/add_community_pr.yml
[b2]: https://github.com/creativecommons/ccos-scripts/actions/workflows/normalize_repos.yml/badge.svg
[l2]: https://github.com/creativecommons/ccos-scripts/actions/workflows/normalize_repos.yml
[b3]: https://github.com/creativecommons/ccos-scripts/actions/workflows/push_data_to_ccos.yml/badge.svg
[l3]: https://github.com/creativecommons/ccos-scripts/actions/workflows/push_data_to_ccos.yml
[b4]: https://github.com/creativecommons/ccos-scripts/actions/workflows/sync_community_team.yml/badge.svg
[l4]: https://github.com/creativecommons/ccos-scripts/actions/workflows/sync_community_team.yml
[b5]: https://github.com/creativecommons/ccos-scripts/actions/workflows/track_backlog.yml/badge.svg
[l5]: https://github.com/creativecommons/ccos-scripts/actions/workflows/track_backlog.yml

[community_pr_yml]: .github/workflows/add_community_pr.yml
[vocab_in_progress]: https://github.com/orgs/creativecommons/projects/13
[norm_pr_yml]: .github/workflows/normalize_repos.yml
[push_ccos_yml]: .github/workflows/push_data_to_ccos.yml
[sync_team_yml]: .github/workflows/sync_community_team.yml
[track_backlog]: .github/workflows/track_backlog.yml
[active_sprint]: https://github.com/orgs/creativecommons/projects/7
[backlog_pending]: https://github.com/orgs/creativecommons/projects/10
[issue-projector]: https://github.com/dhruvkb/issue-projector


## :robot: Automation Authorship

Scripts that commit code or automatically reply to pull requests and issues need to be associated with a GitHub user account. Creative Commons maintains a [cc-open-source-bot](https://github.com/cc-open-source-bot) user for this purpose. This is useful for a few reasons:

- It's ethically important that our community members know when they are talking to a bot instead of a human.
- It makes it easy to audit our automations in the future, because all commits and messages will be associated with the single @cc-open-source-bot user account via the GitHub search, api, etc.
- We won't need to  update automations when there are changes to staff or volunteers.

Using this bot clearly communicates when a commit, comment, or action was performed by an automation. For example, here is some configuration for a workflow using the [Add & Commit](https://github.com/EndBug/add-and-commit) GitHub Action:

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
