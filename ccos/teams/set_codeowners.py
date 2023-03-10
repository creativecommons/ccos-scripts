# Standard library
import datetime
import inspect
import logging
import os
import os.path
import shutil
from pathlib import Path

# Third-party
import git

# First-party/Local
from ccos import log
from ccos.gh_utils import (
    GITHUB_ORGANIZATION,
    GITHUB_TOKEN,
    GITHUB_USERNAME,
    get_cc_organization,
    set_up_github_client,
)
from ccos.teams.set_teams_on_github import map_role_to_team

GIT_USER_NAME = "CC creativecommons.github.io Bot"
GIT_USER_EMAIL = "cc-creativecommons-github-io-bot@creativecommons.org"

WORKING_DIRECTORY = Path("/tmp").resolve()

SYNC_BRANCH = "ct_codeowners"

log_name = os.path.basename(os.path.splitext(inspect.stack()[-1].filename)[0])
logger = logging.getLogger(log_name)
log.reset_handler()


def create_codeowners_for_data(databag):
    set_up_git_user()

    client = set_up_github_client()
    organization = get_cc_organization(client)

    logging.log(logging.INFO, "Identifying and fixing CODEOWNER issues...")
    projects = databag["projects"]
    for project in projects:
        project_name = project["name"]
        logging.log(
            logging.INFO,
            "Identifying and fixing CODEOWNER issues for project"
            f" {project_name}...",
        )

        logging.log(logging.INFO, "Finding all teams...")
        roles = project["roles"]
        teams = get_teams(organization, project_name, roles)
        logging.log(
            logging.INFO,
            f"Found {len(teams)} teams for project {project_name}.",
        )

        logging.log(logging.INFO, "Checking all projects...")
        repos = project["repos"]
        for repo in repos:
            check_and_fix_repo(organization, repo, teams)
    logging.log(log.SUCCESS, "Done")


def set_up_git_user():
    """
    Set the OS environment variables that pertain to Git configuration. These,
    being set on the OS-level, do not need to be configured on a per-repo
    basis.
    """
    logging.log(logging.INFO, "Setting up git user...")
    os.environ["GIT_AUTHOR_NAME"] = GIT_USER_NAME
    os.environ["GIT_AUTHOR_EMAIL"] = GIT_USER_EMAIL
    os.environ["GIT_COMMITTER_NAME"] = GIT_USER_NAME
    os.environ["GIT_COMMITTER_EMAIL"] = GIT_USER_EMAIL


def get_teams(organization, project_name, roles):
    """
    Get all teams corresponding to the Community Team roles for the project.
    Roles with no permissions do not form teams on GitHub and therefore will
    not be represented in the resulting list.

    @param organization: the organization whole teams are being fetched
    @param project_name: the project whose teams are being fetching
    @param roles: the filled roles in the project
    @return: the list of GitHub teams for all Community Team roles
    """
    role_team_map = {
        role: map_role_to_team(organization, project_name, role, False)
        for role in roles.keys()
    }
    return [team for team in role_team_map.values() if team is not None]


def check_and_fix_repo(organization, repo, teams):
    """
    Identify issues with the CODEOWNERS file and rectify them. Missing
    CODEOWNERS files will be created. Incomplete CODEOWNERS files will be
    have new entries appended to them.

    @param organization: the organization to which the repository belongs
    @param repo: the repo to which the CODEOWNERS file being modified belongs
    """

    logging.log(logging.INFO, f"Checking and fixing {repo}...")
    set_up_repo(repo)
    fix_required = False

    if not is_codeowners_present(repo):
        fix_required = True
        codeowners_path = get_codeowners_path(repo)
        logging.log(logging.INFO, " CODEOWNERS does not exist, creating...")
        os.makedirs(codeowners_path.parent, exist_ok=True)
        open(codeowners_path, "a").close()
        logging.log(log.SUCCESS, "                Done.")

    team_mention_map = get_team_mention_map(repo, teams)
    if not all(team_mention_map.values()):
        fix_required = True
        logging.log(logging.INFO, "CODEOWNERS is incomplete, populating...")
        add_missing_teams(repo, team_mention_map)
        logging.log(log.SUCCESS, "                Done.")

    if fix_required:
        logging.log(logging.INFO, "Pushing to GitHub...")
        branch_name = commit_and_push_changes(repo)
        logging.log(log.SUCCESS, f"Pushed to {branch_name}.")

        logging.log(logging.INFO, "Opening a PR...")
        pr = create_pull_request(organization, repo, branch_name)
        logging.log(log.SUCCESS, f"                PR at {pr.url}.")

    logging.log(logging.INFO, "Deleting clone...")
    shutil.rmtree(get_repo_path(repo))
    logging.log(log.SUCCESS, "Done.")

    logging.log(log.SUCCESS, "All is well.")


def commit_and_push_changes(repo):
    """
    Create a new branch and push the CODEOWNER to it. This branch will be named
    in a particular format.

    codeowner branch schema
    ct_codeowners_<timestamp>

    @param repo: the repo to which the CODEOWNERS file being modified belongs
    @return: the name of the branch to which the changes were pushed
    """
    repo = git.Repo(get_repo_path(repo))

    timestamp = int(datetime.datetime.now().timestamp())
    branch_name = f"{SYNC_BRANCH}_{timestamp}"
    repo.git.checkout("HEAD", b=branch_name)

    repo.index.add(items=".github/CODEOWNERS")
    repo.index.commit(message="Sync Community Team to CODEOWNERS")

    origin = repo.remotes.origin
    origin.push(f"{branch_name}:{branch_name}")

    return branch_name


def create_pull_request(organization, repo, branch_name):
    """
    Create a PR from the newly created branch to the base branch of the
    repository containing the required changes to the CODEOWNERS.

    @param organization: the organization to which the repository belongs
    @param repo: the repo to which the CODEOWNERS file being modified belongs
    @param branch_name: the name of the branch containing the CODEOWNERS
                        changes
    """
    repo = organization.get_repo(repo)
    return repo.create_pull(
        title="Sync Community Team to CODEOWNERS",
        body=(
            "This _automated PR_ updates your CODEOWNERS file to mention all "
            "GitHub teams associated with Community Team roles."
        ),
        head=branch_name,
        # default branch could be 'main', 'master', 'prod', or something else
        base=repo.default_branch,
    )


def set_up_repo(repo):
    """
    Clone the repository and pull the main branch.

    @param repo: the repository to set up
    """
    destination_path = get_repo_path(repo)
    if not os.path.isdir(destination_path):
        logging.log(logging.INFO, "Cloning repo...")
        repo = git.Repo.clone_from(
            url=get_github_repo_url_with_credentials(repo),
            to_path=destination_path,
        )
    else:
        logging.log(logging.INFO, "Setting up repo...")
        repo = git.Repo(destination_path)
    origin = repo.remotes.origin
    logging.log(logging.INFO, "Pulling latest code...")
    origin.pull()


def is_codeowners_present(repo):
    """
    Check whether the repository has a CODEOWNERS file.

    @param repo: the repository in which to check the existence of CODEOWNERS
    @return: True if a CODEOWNERS file exists, False otherwise
    """
    codeowners_path = get_codeowners_path(repo)
    return codeowners_path.exists() and codeowners_path.is_file()


def get_team_mention_map(repo, teams):
    """
    Map the team slugs to whether they have been mentioned in the CODEOWNERS
    file in any capacity.

    @param repo: the repo to which the CODEOWNERS file being modified belongs
    @param teams: all the GitHub teams for all Community Teams of a project
    @return: a dictionary of team slugs and their mentions
    """
    codeowners_path = get_codeowners_path(repo)
    with open(codeowners_path) as codeowners_file:
        contents = codeowners_file.read()
    return {team.slug: mentionified(team.slug) in contents for team in teams}


def add_missing_teams(repo, team_mention_map):
    """
    Add the mention forms for all missing teams in a new line.

    @param repo: the repo to which the CODEOWNERS file being modified belongs
    @param team_mention_map: the dictionary of team slugs and their mentions
    """
    missing_team_slugs = [
        team_slug
        for team_slug in team_mention_map.keys()
        if not team_mention_map[team_slug]
    ]
    codeowners_path = get_codeowners_path(repo)
    with open(codeowners_path, "a") as codeowners_file:
        addendum = generate_ideal_codeowners_rule(missing_team_slugs)
        codeowners_file.write(addendum)
        codeowners_file.write("\n")


def generate_ideal_codeowners_rule(team_slugs):
    """
    Generate an ideal CODEOWNERS rule for the given set of roles. Assigns all
    files using the wildcard expression '*' to the given roles.

    @param team_slugs: the set of team slugs to be added to the CODEOWNERS file
    @return: the line that should be added to the CODEOWNERS file
    """
    combined_team_slugs = " ".join(map(mentionified, team_slugs))
    return f"* {combined_team_slugs}"


def get_github_repo_url_with_credentials(repo):
    """
    Get the HTTPS URL to the repository which has the username and a GitHub
    token for authentication.

    @param repo: the name of the repository
    @return: the authenticated URL to the repo
    """
    return (
        f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}"
        f"@github.com/{GITHUB_ORGANIZATION}/{repo}.git"
    )


def get_repo_path(repo):
    """
    Get the fully qualified absolute path to the repository on the local file
    system. Repositories are cloned into eponymous directories inside the
    working directory.

    @param repo: the name of the repository
    @return: the absolute path to cloned repository on local FS
    """
    return WORKING_DIRECTORY.joinpath(repo)


def get_codeowners_path(repo):
    """
    Get the fully qualified absolute path to the CODEOWNERS file inside the
    given repository. By convention the file should be located inside the
    '.github/' directory in the repository.

    @param repo: the name of the repository
    @return: the absolute path to the CODEOWNERS file
    """
    return get_repo_path(repo).joinpath(".github", "CODEOWNERS")


def mentionified(team_slug):
    """
    Get the mention form of the given team. Mention forms are generated by
    prefixing the organization to the team slug.

    mention form schema
    @<organization>/<team slug>

    @param team_slug: the slug of the team to mention
    @return: the mentionable form of the given team slug
    """
    return f"@{GITHUB_ORGANIZATION}/{team_slug}"
