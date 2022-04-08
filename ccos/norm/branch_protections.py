EXEMPT_REPOSITORIES = [
    # non-engineering repo
    "australian-chapter",
    # non-engineering repo
    "cc-cert-core",
    # non-engineering repo
    "cc-cert-edu",
    # non-engineering repo
    "cc-cert-gov",
    # non-engineering repo
    "cc-cert-lib",
    # exempted to allow transifex updates
    "cc.i18n",
    # exempted to allow community maintainer to self-merge PRs
    "ccsearch-browser-extension",
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
    "cccatalog-api": ["Style", "Tests"],
    "cccatalog-frontend": ["Run CI tests"],
    "creativecommons.github.io-source": ["continuous-integration/travis-ci"],
    "fonts": [
        "Lint",
        "Unit tests",
        "Build",
        "netlify/cc-fonts/deploy-preview",
    ],
    "vocabulary": [
        "Lint",
        "Unit tests",
        "Build",
        "netlify/cc-vocabulary/deploy-preview",
    ],
    "vue-vocabulary": [
        "Lint",
        "Unit tests",
        "Build",
        "netlify/cc-vue-vocabulary/deploy-preview",
    ],
}
