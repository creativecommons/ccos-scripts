BRANCH_PROTECTION_EXEMPT_REPOSITORIES = [
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
    # exempted for bot pushes to master
    "creativecommons.github.io-source",
    # exempted for bot pushes to master
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

BRANCH_PROTECTION_REQUIRED_STATUS_CHECK_MAP = {
    "cccatalog-api": ["continuous-integration/travis-ci"],
    "cccatalog-frontend": ["ci/circleci: lint", "ci/circleci: unit"],
    "creativecommons.github.io-source": ["continuous-integration/travis-ci"],
    "fonts": [
        "ci/circleci: lint",
        "ci/circleci: build",
        "netlify/cc-fonts/deploy-preview",
    ],
    "vocabulary": [
        "ci/circleci: lint",
        "ci/circleci: test",
        "ci/circleci: build",
        "netlify/cc-vocabulary/deploy-preview",
    ],
    "vue-vocabulary": [
        "ci/circleci: lint",
        "ci/circleci: unit",
        "netlify/cc-vue-vocabulary/deploy-preview",
    ],
}