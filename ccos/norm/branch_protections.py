# The following repositories are exempt from both branch protections and issue
# label validation:
EXEMPT_REPOSITORIES = [
    # special purpose repo
    "australian-chapter",
    # exempted for bot pushes to default branch
    "creativecommons.github.io-source",
    # exempted for bot pushes to default branch
    "creativecommons.github.io",
    # special purpose repo
    "global-network-strategy",
    # special purpose repo
    "network-platforms",
    # special purpose repo
    "sre-wiki-js",
    # special purpose repo
    "tech-support",
]

REQUIRED_STATUS_CHECK_MAP = {
    "creativecommons.github.io-source": ["Build and Deploy CC Open Source"],
}
