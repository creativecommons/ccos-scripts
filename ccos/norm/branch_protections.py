EXEMPT_REPOSITORIES = [
    # non-engineering repo
    "australian-chapter",
    # exempted to allow transifex updates
    "cc.i18n",
    # exempted for bot pushes to default branch
    "creativecommons.github.io-source",
    # exempted for bot pushes to default branch
    "creativecommons.github.io",
    # non-engineering repo
    "global-network-strategy",
    # non-engineering repo
    "network-platforms",
    # non-engineering repo
    "sre-wiki-js",
    # non-engineering repo
    "tech-support",
]

REQUIRED_STATUS_CHECK_MAP = {
    "creativecommons.github.io-source": ["Build and Deploy CC Open Source"],
    "vocabulary": [
        "Lint",
        "Unit tests",
        "Build",
        "netlify/cc-vocabulary/deploy-preview",
    ],
}
