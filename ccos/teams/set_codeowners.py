# Standard library
import datetime
import inspect
import logging
import os
import os.path
from pathlib import Path
from tempfile import TemporaryDirectory

# Third-party
import git

# First-party/Local
from ccos import log
from ccos.gh_utils import (
    GITHUB_ORGANIZATION,
    get_cc_organization,
    get_credentials,
    set_up_github_client,
)
from ccos.teams.set_teams_on_github import map_role_to_team

GIT_USER_NAME = "CC creativecommons.github.io Bot"
GIT_USER_EMAIL = "cc-creativecommons-github-io-bot@creativecommons.org"

SYNC_BRANCH = "ct_codeowners"

log_name = os.path.basename(os.path.splitext(inspect.stack()[-1].filename)[0])
logger = logging.getLogger(log_name)
log.reset_handler()


def create_codeowners_for_data(databag):
    set_up_git_user()
    github_client = set_up_github_client()
    organization = get_cc_organization(github_client)

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
        with TemporaryDirectory() as temp_dir:
            for repo_name in repos:
                check_and_fix_repo(organization, repo_name, teams, temp_dir)
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


def check_and_fix_repo(organization, repo_name, teams, temp_dir):
    """
    Identify issues with the CODEOWNERS file and rectify them. Missing
    CODEOWNERS files will be created. Incomplete CODEOWNERS files will be
    have new entries appended to them.

    @param organization: the organization to which the repository belongs
    @param repo: the repo to which the CODEOWNERS file being modified belongs
    """

    logging.log(logging.INFO, f"Checking and fixing {repo_name}...")
    repo_dir = os.path.join(temp_dir, repo_name)
    gh_repo = organization.get_repo(repo_name)
    clone_url = get_github_repo_url_with_credentials(repo_name)
    local_repo = set_up_repo(clone_url, repo_dir)
    codeowners_path = Path(os.path.join(repo_dir, ".github", "CODEOWNERS"))
    fix_required = False

    if not codeowners_path.exists() and codeowners_path.is_file():
        fix_required = True
        logging.log(logging.INFO, "CODEOWNERS does not exist, creating...")
        os.makedirs(codeowners_path.parent, exist_ok=True)
        open(codeowners_path, "a").close()
        logging.log(log.SUCCESS, "Done.")

    team_mention_map = get_team_mention_map(codeowners_path, teams)
    if not all(team_mention_map.values()):
        fix_required = True
        logging.log(logging.INFO, "CODEOWNERS is incomplete, populating...")
        add_missing_teams(codeowners_path, team_mention_map)
        logging.log(log.SUCCESS, "Done.")

    if fix_required:
        logging.log(logging.INFO, "Pushing to GitHub...")
        branch_name = commit_and_push_changes(local_repo, codeowners_path)
        logging.log(log.SUCCESS, f"Pushed to {branch_name}.")

        logging.log(logging.INFO, "Opening a PR...")
        pr = create_pull_request(gh_repo, branch_name)
        logging.log(log.SUCCESS, f"PR at {pr.url}.")

    logging.log(log.SUCCESS, "Done.")

    logging.log(log.SUCCESS, "All is well.")


def commit_and_push_changes(local_repo, codeowners_path):
    """
    Create a new branch and push the CODEOWNER to it. This branch will be named
    in a particular format.

    codeowner branch schema
    ct_codeowners_<timestamp>

    @param local_repo: GitPython Repo instance for the repo to which the
                       CODEOWNERS file being modified belongs
    @param codeowners_path: the path of the CODEOWNERS file
    @return: the name of the branch to which the changes were pushed
    """
    timestamp = int(datetime.datetime.now().timestamp())
    branch_name = f"{SYNC_BRANCH}_{timestamp}"
    local_repo.git.checkout("HEAD", b=branch_name)

    local_repo.index.add(items=codeowners_path)
    local_repo.index.commit(message="Sync Community Team(s) to CODEOWNERS")

    origin = local_repo.remotes.origin
    origin.push(f"{branch_name}:{branch_name}")

    return branch_name


def create_pull_request(gh_repo, branch_name):
    """
    Create a PR from the newly created branch to the base branch of the
    repository containing the required changes to the CODEOWNERS.

    @param gh_repo: PyGithub Repository object
    @param branch_name: the name of the branch containing the CODEOWNERS
                        changes
    """
    return gh_repo.create_pull(
        title="Sync Community Team to CODEOWNERS",
        body=(
            "This _automated PR_ updates your CODEOWNERS file to mention all "
            "GitHub teams associated with Community Team roles."
        ),
        head=branch_name,
        # default branch could be 'main', 'master', 'prod', or something else
        base=gh_repo.default_branch,
    )


def set_up_repo(clone_url, repo_dir):
    """
    Clone the repository and pull the main branch.

    @param clone_url: the authenticated URL to the GitHub repo
    @param repo_dir: the local directory for the repository
    @return: GitPython Repo instance
    """
    logging.log(logging.INFO, "Cloning repo...")
    local_repo = git.Repo.clone_from(url=clone_url, to_path=repo_dir)
    return local_repo


def get_team_mention_map(codeowners_path, teams):
    """
    Map the team slugs to whether they have been mentioned in the CODEOWNERS
    file in any capacity.

    @param codeowners_path: the path of the CODEOWNERS file
    @param teams: all the GitHub teams for all Community Teams of a project
    @return: a dictionary of team slugs and their mentions
    """
    with open(codeowners_path) as codeowners_file:
        contents = codeowners_file.read()
    return {team.slug: mentionified(team.slug) in contents for team in teams}


def add_missing_teams(codeowners_path, team_mention_map):
    """
    Add the mention forms for all missing teams in a new line.

    @param codeowners_path: the path of the CODEOWNERS file
    @param team_mention_map: the dictionary of team slugs and their mentions
    """
    missing_team_slugs = [
        team_slug
        for team_slug in team_mention_map.keys()
        if not team_mention_map[team_slug]
    ]
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


def get_github_repo_url_with_credentials(repo_name):
    """
    Get the HTTPS URL to the repository which has the username and a GitHub
    token for authentication.

    @param repo_name: the name of the repository
    @return: the authenticated URL to the GitHub repo
    """
    github_username, github_token = get_credentials()
    return (
        f"https://{github_username}:{github_token}"
        f"@github.com/{GITHUB_ORGANIZATION}/{repo_name}.git"
    )


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
