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

DEPLOYMENT_BRANCHES = ['staging', 'production', 'taskcluster-rework']


NIX_BIN_DIR = os.environ.get("NIX_BIN_DIR", "")  # must end with /
OPENSSL_BIN_DIR = os.environ.get("OPENSSL_BIN_DIR", "")  # must end with /
OPENSSL_ETC_DIR = os.environ.get("OPENSSL_ETC_DIR", "")  # must end with /
POSTGRESQL_BIN_DIR = os.environ.get("POSTGRESQL_BIN_DIR", "")  # must end with /

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
    VERSION = f.read().strip()


# TODO: below data should be placed in src/<app>/default.nix files alongside
APPS = {
    'postgresql': {
        'run': 'POSTGRESQL',
        'run_options': {
            'port': 9000,
            'data_dir': os.path.join(TMP_DIR, 'postgresql'),
        },
    },
    'releng-archiver': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8005,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-archiver',
                'url': 'https://archiver.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'releng-production-archiver',
                'url': 'https://archiver.mozilla-releng.net',
            },
        },
    },
    'releng-clobberer': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8001,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-clobberer',
                'url': 'https://clobberer.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'releng-production-clobberer',
                'url': 'https://clobberer.mozilla-releng.net',
            },
        },
    },
    'releng-docs': {
        'run': 'SPHINX',
        'run_options': {
            'schema': 'http',
            'port': 7000,
        },
        'deploy': 'S3',
        'deploy_option': {
            'staging': {
                's3_bucket': 'releng-staging-docs',
                'url': 'https://docs.staging.mozilla-releng.net',
            },
            'production': {
                's3_bucket': 'releng-production-docs',
                'url': 'https://docs.mozilla-releng.net',
            },
        }
    },
    'releng-frontend': {
        'run': 'ELM',
        'run_options': {
            'port': 8000,
        },
        'requires': [
            'releng-docs',
            'releng-clobberer',
            'releng-tooltool',
            'releng-treestatus',
            'releng-mapper',
            'releng-archiver',
        ],
        'deploy': 'S3',
        'deploy_option': {
            'staging': {
                's3_bucket': 'releng-staging-frontend',
                'url': 'https://staging.mozilla-releng.net',
                'csp': [
                    'https://auth.taskcluster.net',
                ],
            },
            'production': {
                's3_bucket': 'releng-production-frontend',
                'url': 'https://mozilla-releng.net',
                'csp': [
                    'https://auth.taskcluster.net',
                ],
            },
        },
    },
    'releng-mapper': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8004,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-mapper',
                'url': 'https://mapper.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'releng-production-mapper',
                'url': 'https://mapper.mozilla-releng.net',
            },
        },
    },
    'releng-tooltool': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8002,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-tooltool',
                'url': 'https://tooltool.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'releng-production-tooltool',
                'url': 'https://tooltool.mozilla-releng.net',
            },
        },
    },
    'releng-treestatus': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8003,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-treestatus',
                'url': 'https://treestatus.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'releng-production-treestatus',
                'url': 'https://treestatus.mozilla-releng.net',
            },
        },
    },
    # TODO: shipit_bot_uplift
    # TODO: shipit_code_coverage
    'shipit-frontend': {
        'run': 'ELM',
        'run_options': {
            'port': 8010,
            'envs': {
                'WEBPACK_BUGZILLA_URL': 'https://bugzilla-dev.allizom.org',
            }
        },
        'requires': [
            'uplift',
        ],
        'deploy': 'S3',
        'deploy_option': {
            'staging': {
                's3_bucket': 'shipit-staging-frontend',
                'url': 'https://shipit.staging.mozilla-releng.net',
                'envs': {
                    'WEBPACK_BUGZILLA_URL': 'https://bugzilla.mozilla.org',
                },
                'csp': [
                    'https://auth.taskcluster.net',
                    'https://bugzilla.mozilla.org',
                ],
            },
            'production': {
                's3_bucket': 'shipit-production-frontend',
                'url': 'https://shipit.mozilla-releng.net',
                'envs': {
                    'WEBPACK_BUGZILLA_URL': 'https://bugzilla.mozilla.org',
                },
                'csp': [
                    'https://auth.taskcluster.net',
                    'https://bugzilla.mozilla.org',
                ],
            },
        },
    },
    'shipit-pipeline': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8012,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'shipit-staging-pipeline',
                'url': 'https://pipeline.shipit.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'shipit-production-pipeline',
                'url': 'https://pipeline.shipit.mozilla-releng.net',
            },
        },
    },
    # TODO: shipit_pulse_listener
    # TODO: shipit_risk_assessment
    'shipit-signoff': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8013,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'shipit-staging-signoff',
                'url': 'https://signoff.shipit.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'shipit-production-signoff',
                'url': 'https://signoff.shipit.mozilla-releng.net',
            },
        },
    },
    # TODO: shipit_static_analysis
    'shipit-taskcluster': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8014,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'shipit-staging-taskcluster',
                'url': 'https://taskcluster.shipit.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'shipit-production-taskcluster',
                'url': 'https://taskcluster.shipit.mozilla-releng.net',
            },
        },
    },
    'shipit-uplift': {
        'checks': [
            ('Checking code quality', 'flake8'),
            ('Running tests', 'pytest tests/'),
        ],
        'run': 'FLASK',
        'run_options': {
            'port': 8011,
        },
        'requires': [
            'postgresql',
        ],
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'shipit-staging-dashboard',
                'url': 'https://uplift.shipit.staging.mozilla-releng.net',
            },
            'production': {
                'heroku_app': 'shipit-production-dashboard',
                'url': 'https://uplift.shipit.mozilla-releng.net',
            },
        },
    },
}
