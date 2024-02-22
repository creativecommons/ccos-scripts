#!/bin/bash
#
# Notes:
#
# --workflows required to avoid errors.
# See: https://github.com/nektos/act/issues/1993
#
#
#### SETUP ####################################################################
set -o errtrace
set -o nounset

# https://en.wikipedia.org/wiki/ANSI_escape_code
E0="$(printf "\e[0m")"          # reset
E30="$(printf "\033[30m")"      # black foreground
E31="$(printf "\e[31m")"      # red foreground
E107="$(printf "\033[107m")"    # bright white background


error_exit() {
    # Echo error message and exit with error
    echo -e "${E31}ERROR:${E0} ${*}" 1>&2
    exit 1
}


header() {
    # Print 80 character wide black on white heading
    printf "${E30}${E107} %-71s$(date '+%T') ${E0}\n" "${@}"
}


run_act() {
    act --container-architecture linux/amd64 \
        --detect-event \
        --rm \
        --secret ADMIN_ASANA_TOKEN \
        --secret ADMIN_GITHUB_TOKEN \
        "${@}"
}


header 'Confirm prerequisites'
# macOS
if [[ $(uname -s) != 'Darwin' ]]
then
    error_exit 'This script only supports macOS'
else
    echo 'Operatings system is macOS'
fi
# act
if ! command -v act >/dev/null
then
    error_exit 'act must be installed (`act` not found in PATH)'
else
    echo -n 'act is installed: '
    act --version
fi
# Docker
if ! command -v docker >/dev/null
then
    error_exit 'Docker must be installed (`docker` not found in PATH)'
else
    echo -n 'Docker is installed: '
    docker --version
fi
# ADMIN_ASANA_TOKEN
if [[ -z "${ADMIN_ASANA_TOKEN:-}" ]]
then
    error_exit 'environment variable missing: ADMIN_ASANA_TOKEN'
else
    echo 'Environment variable is set: ADMIN_ASANA_TOKEN'
fi
# ADMIN_GITHUB_TOKEN
if [[ -z "${ADMIN_GITHUB_TOKEN:-}" ]]
then
    error_exit 'environment variable missing: ADMIN_GITHUB_TOKEN'
else
    echo 'Environment variable is set: ADMIN_GITHUB_TOKEN'
fi
echo


header 'Ensuring docker is running'
if [[ -S /var/run/docker.sock ]]
then
    echo -n .
    for _ in {1..5}
    do
        echo -n .
        sleep 0.2
    done
    echo
else
    open -a Docker
    while [[ ! -S /var/run/docker.sock ]]
    do
        echo -n .
        sleep 0.2
    done
    for _ in {1..40}
    do
        echo -n .
        sleep 0.2
    done
    echo
fi
echo


header 'List workflows'
run_act --list
echo


header 'Test: Push data to CC Open Source'
run_act --workflows .github/workflows/push_data_to_ccos.yml \
    --job push_data
echo


header 'Test: Sync Community Teams with GitHub'
run_act --workflows .github/workflows/sync_community_teams.yml \
    --job sync_community_teams
echo


header 'Test: Manage issues and pull requests in projects'
run_act --workflows .github/workflows/manage_issues.yml \
    --job manage_issues_and_pull_requests
echo


header 'Test: Normalize Repos'
run_act --workflows .github/workflows/normalize_repos.yml \
    --job normalize_repos
echo
