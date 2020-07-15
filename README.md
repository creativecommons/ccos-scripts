# CC Open Source Scripts

These are scripts used to maintain various pieces of CC's open source community
infrastructure.


## Scripts

Please see the individual README files in the folder for each script for
information about that script.

| Directory Name                    | Script Purpose                                                                  |
| --------------------------------- | ------------------------------------------------------------------------------- |
| [`normalize_repos`][norm]         | Ensures that all CC repos have standard labels and branch protections           |
| [`push_data_to_ccos`][push_to_ccos]  | Generates various pages with dynamic data on [CC Open Source][ccos] |


## Workflows
| YML File Name                   | Workflow Purpose                                                        |
| -------------------------------- | --------------------------------------------------------------------- |
| [`add_community_pr.yml`][community_pr_yml]        |  Runs hourly at 5 minutes past every hour UTC and add community PRs to [Active Sprint – CC Search](https://github.com/orgs/creativecommons/projects/7) and [Vocabulary Planning]((https://github.com/orgs/creativecommons/projects/13) |
| [`normalize_repos.yml`][norm_pr_yml]        |  Runs daily at 00:00 UTC and whenever someone pushes to master branch and uses [`normalize_repos`][norm]   |
| [`push_data_to_ccos.yml`][push_ccos_yml]        | Runs daily at 00:00 UTC and whenever someone pushes to master branch and uses [`push_data_to_ccos`][push_to_ccos] |


[community_pr_yml]:.github/workflows/add_community_pr.yml
[norm_pr_yml]:.github/workflows/normalize_repos.yml
[push_ccos_yml]:.github/workflows/push_data_to_ccos.yml

[norm]:normalize_repos/
[push_to_ccos]:push_data_to_ccos/

[ccos]: httpe://opensource.creativecommons.org/


## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"
