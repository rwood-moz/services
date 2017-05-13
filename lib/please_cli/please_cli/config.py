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


NIX_BIN_DIR = ""  # must end with /

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
    VERSION = f.read().strip()

# TODO: below data should be placed in src/<app>/default.nix files alongside
APPS = {
    'postgresql': {
        'run': 'CLI',
        'run_options': {
            'pre_commands': [
                'please_cli.misc.initdb',
            ],
            'cli_args': [
                ('-D', TMP_DIR + '/postgres'),
                ('-h', 'localhost'),
                ('-p', 9000),
            ],
        },
    },
    'releng-archiver': {
        'run': 'FLASK',
        'run_options': {
            'port': 8005,
        },
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-archiver',
            },
            'production': {
                'heroku_app': 'releng-production-archiver',
            },
        },
    },
    'releng-clobberer': {
        'run': 'FLASK',
        'run_options': {
            'port': 8001,
        },
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-clobberer',
            },
            'production': {
                'heroku_app': 'releng-production-clobberer',
            },
        },
    },
    'releng-docs': {
        'run': 'SPHINX',
        'run_options': {
            'port': 7000,
        },
        'deploy': 'S3',
        'deploy_option': {
            'staging': {
                's3_bucket': 'releng-staging-docs',
            },
            'production': {
                's3_bucket': 'releng-production-docs',
            },
        }
    },
    'releng-frontend': {
        'run': 'ELM',
        'run_options': {
            'port': 8000,
        },
        'deploy': 'S3',
        'deploy_option': {
            'staging': {
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
            'production': {
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
        },
    },
    'releng-mapper': {
        'run': 'FLASK',
        'run_options': {
            'port': 8004,
        },
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-mapper',
            },
            'production': {
                'heroku_app': 'releng-production-mapper',
            },
        },
    },
    'releng-tooltool': {
        'run': 'FLASK',
        'run_options': {
            'port': 8002,
        },
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-tooltool',
            },
            'production': {
                'heroku_app': 'releng-production-tooltool',
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
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'releng-staging-treestatus',
            },
            'production': {
                'heroku_app': 'releng-production-treestatus',
            },
        },
    },
    # TODO: shipit_bot_uplift
    # TODO: shipit_code_coverage
    'shipit-frontend': {
        'run': 'ELM',
        'run_options': {
            'port': 8010,
        },
        'deploy': 'S3',
        'deploy_option': {
            'staging': {
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
            'production': {
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
        },
    },
    'shipit-pipeline': {
        'run': 'FLASK',
        'run_options': {
            'port': 8012,
        },
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'shipit-staging-pipeline',
            },
            'production': {
                'heroku_app': 'shipit-production-pipeline',
            },
        },
    },
    # TODO: shipit_pulse_listener
    # TODO: shipit_risk_assessment
    'shipit-signoff': {
        'run': 'FLASK',
        'run_options': {
            'port': 8013,
        },
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'shipit-staging-signoff',
            },
            'production': {
                'heroku_app': 'shipit-production-signoff',
            },
        },
    },
    # TODO: shipit_static_analysis
    'shipit-taskcluster': {
        'run': 'FLASK',
        'run_options': {
            'port': 8014,
        },
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'shipit-staging-taskcluster',
            },
            'production': {
                'heroku_app': 'shipit-production-taskcluster',
            },
        },
    },
    'shipit-uplift': {
        'run': 'FLASK',
        'run_options': {
            'port': 8011,
        },
        'deploy': 'HEROKU',
        'deploy_option': {
            'staging': {
                'heroku_app': 'shipit-staging-dashboard',
            },
            'production': {
                'heroku_app': 'shipit-production-dashboard',
            },
        },
    },
}
