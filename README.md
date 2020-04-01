# CC Open Source Scripts

These are scripts used to maintain various pieces of CC's open source community
infrastructure.


## Scripts

Please see the individual README files in the folder for each script for
information about that script.

| Directory Name                   | Script Purpose                                                        |
| -------------------------------- | --------------------------------------------------------------------- |
| [`normalize_repos`][norm]        | Ensures that all CC repos have standard labels and branch protections |
| [`generate_projects_page`][proj] | Generates the ["Projects" page on CC Open Source][osproj]             |


## Workflows
| YML File Name                   | Workflow Purpose                                                        |
| -------------------------------- | --------------------------------------------------------------------- |
| [`generate_projects_page.yml`][gen_proj_yml]        |  Runs daily at 00:00 UTC and whenever someone pushes to master branch and uses [`normalize_repos`][norm]   |
| [`normalize_repos.yml`][norm_pr_yml]        | Runs daily at 00:00 UTC and whenever someone pushes to master branch and uses [`generate_projects_page`][proj] |
| [`add_community_pr.yml`][community_pr_yml]        |  Runs hourly at 5 minutes past every hour UTC and add community PRs to [Active Sprint – CC Search](https://github.com/orgs/creativecommons/projects/7) |


[community_pr_yml]:.github/workflows/add_community_pr.yml
[gen_proj_yml]:.github/workflows/generate_projects_page.yml
[norm_pr_yml]:.github/workflows/normalize_repos.yml

[norm]:normalize_repos/
[proj]:generate_projects_page/
[osproj]:https://opensource.creativecommons.org/contributing-code/projects/


## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"
