# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os
import click

CWD_DIR = os.path.abspath(os.getcwd())

NO_ROOT_DIR_ERROR = '''Project root directory couldn't be detected.

`please` file couln't be found in any of the following folders:
%s
'''


ROOT_DIR = None
_folders = []
for item in reversed(CWD_DIR.split(os.sep)):
    item_dir = '/' + CWD_DIR[:CWD_DIR.find(item) + len(item)][1:]
    _folders.append(item_dir)
    if os.path.isfile(os.path.join(item_dir, 'please')):
        ROOT_DIR = item_dir
        break

if ROOT_DIR is None:
    raise click.ClickException(NO_ROOT_DIR_ERROR % '\n - '.join(_folders))

DOCKER_REGISTRY = "https://index.docker.com"
CACHE_URL = "https://cache.mozilla-releng.net"

SRC_DIR = os.path.join(ROOT_DIR, 'src')
TMP_DIR = os.path.join(ROOT_DIR, 'tmp')
APPS = [i.replace('_', '-') for i in os.listdir(SRC_DIR)]

DEPLOYMENT_BRANCHES = ['staging', 'production', 'taskcluster-rework']


NIX_BIN_DIR = ""  # must end with /

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
    VERSION = f.read().strip()

# XXX: below data should be placed in src/<app>/default.nix
DEPLOY_STAGING = {
    'releng-docs': {
        's3_bucket': 'releng-staging-docs',
    },
    'releng-frontend': {
        's3_bucket': 'releng-staging-frontend',
        'flags': {
            'version': 'v' + VERSION,
            'docs-url': 'https://docs.staging.mozilla-releng.net',
            'clobberer-url': 'https://clobberer.staging.mozilla-releng.net',
            'tooltool-url': 'https://tooltool.staging.mozilla-releng.net',
            'treestatus-url': 'https://treestatus.staging.mozilla-releng.net',
            'mapper-url': 'https://mapper.staging.mozilla-releng.net',
            'archiver-url': 'https://archiver.staging.mozilla-releng.net',
        },
        'csp': [
            'https://auth.taskcluster.net',
            'https://clobberer.staging.mozilla-releng.net',
            'https://tooltool.staging.mozilla-releng.net',
            'https://treestatus.staging.mozilla-releng.net',
            'https://mapper.staging.mozilla-releng.net',
            'https://archiver.staging.mozilla-releng.net',
        ],
    },
    'shipit-frontend': {
        's3_bucket': 'shipit-staging-frontend',
        'flags': {
            'version': 'v' + VERSION,
            'uplift-url': 'https://dashboard.shipit.staging.mozilla-releng.net',
            'bugzilla-url': 'https://bugzilla.mozilla.org',
        },
        'csp': [
            'https://auth.taskcluster.net',
            'https://dashboard.shipit.staging.mozilla-releng.net',
            'https://bugzilla.mozilla.org',
        ],
    },
    'releng-clobberer': {
        'heroku_app': 'releng-staging-clobberer',
    },
    'releng-tooltool': {
        'heroku_app': 'releng-staging-tooltool',
    },
    'releng-treestatus': {
        'heroku_app': 'releng-staging-treestatus',
    },
    'releng-mapper': {
        'heroku_app': 'releng-staging-mapper',
    },
    'releng-archiver': {
        'heroku_app': 'releng-staging-archiver',
    },
    'shipit-uplift': {
        'heroku_app': 'shipit-staging-dashboard',
    },
    'shipit-pipeline': {
        'heroku_app': 'shipit-staging-pipeline',
    },
    'shipit-signoff': {
        'heroku_app': 'shipit-staging-signoff',
    },
    'shipit-taskcluster': {
        'heroku_app': 'shipit-staging-taskcluster',
    },
}

DEPLOY_PRODUCTION = {
    'releng-docs': {
        's3_bucket': 'releng-production-docs',
    },
    'releng-frontend': {
        's3_bucket': 'releng-production-frontend',
        'flags': {
            'version': 'v' + VERSION,
            'docs-url': 'https://docs.mozilla-releng.net',
            'clobberer-url': 'https://clobberer.mozilla-releng.net',
            'tooltool-url': 'https://tooltool.mozilla-releng.net',
            'treestatus-url': 'https://treestatus.mozilla-releng.net',
            'mapper-url': 'https://mapper.mozilla-releng.net',
            'archiver-url': 'https://archiver.mozilla-releng.net',
        },
        'csp': [
            'https://auth.taskcluster.net',
            'https://clobberer.mozilla-releng.net',
            'https://tooltool.mozilla-releng.net',
            'https://treestatus.mozilla-releng.net',
            'https://mapper.mozilla-releng.net',
            'https://archiver.mozilla-releng.net',
        ],
    },
    'shipit-frontend': {
        's3_bucket': 'shipit-production-frontend',
        'flags': {
            'version': 'v' + VERSION,
            'uplift-url': 'https://dashboard.shipit.mozilla-releng.net',
        },
        'csp': [
            'https://auth.taskcluster.net',
            'https://dashboard.shipit.mozilla-releng.net',
            'https://bugzilla.mozilla.org',
        ],
    },
    'releng-clobberer': {
        'heroku_app': 'releng-production-clobberer',
    },
    'releng-tooltool': {
        'heroku_app': 'releng-production-tooltool',
    },
    'releng-treestatus': {
        'heroku_app': 'releng-production-treestatus',
    },
    'releng-mapper': {
        'heroku_app': 'releng-production-mapper',
    },
    'releng-archiver': {
        'heroku_app': 'releng-production-archiver',
    },
    'shipit-uplift': {
        'heroku_app': 'shipit-production-dashboard',
    },
    'shipit-pipeline': {
        'heroku_app': 'shipit-production-pipeline',
    },
    'shipit-signoff': {
        'heroku_app': 'shipit-production-signoff',
    },
    'shipit-taskcluster': {
        'heroku_app': 'shipit-production-taskcluster',
    },
}
