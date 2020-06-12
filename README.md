# CC Open Source Scripts

These are scripts used to maintain various pieces of CC's open source community
infrastructure.


## Scripts

Please see the individual README files in the folder for each script for
information about that script.

| Directory Name                    | Script Purpose                                                                  |
| --------------------------------- | ------------------------------------------------------------------------------- |
| [`normalize_repos`][norm]         | Ensures that all CC repos have standard labels and branch protections           |
| [`generate_projects_page`][proj]  | Generates the ["Projects" page on CC Open Source][osproj]                       |
| [`community_teams_list_page`][ctlist] | Generates the ["Community Teams Members" page on CC Open Source][ctlistpage] |
| [`search_roadmap_export`][search] | Exports the `CC Search Roadmap` Asana project to opensource.creativecommons.org |


## Workflows
| YML File Name                   | Workflow Purpose                                                        |
| -------------------------------- | --------------------------------------------------------------------- |
| [`add_community_pr.yml`][community_pr_yml]        |  Runs hourly at 5 minutes past every hour UTC and add community PRs to [Active Sprint – CC Search](https://github.com/orgs/creativecommons/projects/7) |
| [`community_teams_list_page.yml`][community_teams_yml]        | Runs daily at 00:00 UTC and whenever someone pushes to master branch and uses [`community_teams_list_page`][[ct]] |
| [`generate_projects_page.yml`][gen_proj_yml]        | Runs daily at 00:00 UTC and whenever someone pushes to master branch and uses [`generate_projects_page`][proj] |
| [`normalize_repos.yml`][norm_pr_yml]        |  Runs daily at 00:00 UTC and whenever someone pushes to master branch and uses [`normalize_repos`][norm]   |
| [`search_roadmap_export.yml`][search_roadmap_yml]        | Runs daily at 00:00 UTC and whenever someone pushes to master branch and uses [`search_roadmap_export`][search] |


[community_pr_yml]:.github/workflows/add_community_pr.yml
[community_teams_yml]:.github/workflows/community_teams_list_page.yml
[gen_proj_yml]:.github/workflows/generate_projects_page.yml
[norm_pr_yml]:.github/workflows/normalize_repos.yml
[search_roadmap_yml]:.github/workflows/search_roadmap_export.yml

[ct]: community_teams_list_page/
[norm]:normalize_repos/
[proj]:generate_projects_page/
[search]:search_roadmap_export/

[ctlistpage]: httpe://opensource.creativecommons.org/community/community-teams/members
[osproj]:https://opensource.creativecommons.org/contributing-code/projects/



## License

- [`LICENSE`](LICENSE) (Expat/[MIT][mit] License)

[mit]: http://www.opensource.org/licenses/MIT "The MIT License | Open Source Initiative"
