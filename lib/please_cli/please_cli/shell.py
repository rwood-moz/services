# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import click
import os

import cli_common.log
import please_cli.config


log = cli_common.log.get_logger(__name__)

CMD_HELP = '''

Enter development environment of an APPLICATION.

\b
APPLICATIONS:
{apps}

EXAMPLES:

  1. for Flask / Connexion application:

  \b
  ~/d/m/services % ./please shell releng-treestatus
  [nix-shell] ~/d/m/s/s/releng_treestatus % flask run
  [nix-shell] ~/d/m/s/s/releng_treestatus % connexion run connexion run releng_treestatus/api.yml
  [nix-shell] ~/d/m/s/s/releng_treestatus % ipython
  Python 3.5.3 (default, Jan 17 2017, 07:57:56)
  In [1]: import releng_treestatus
  In [2]: exit
  [nix-shell] ~/d/m/s/s/releng_treestatus % exit

  2. for Elm application:

  \b
  ~/d/m/services % ./please shell releng-frontend
  [nix-shell] ~/d/m/s/s/releng_frontend % elm repl
  [nix-shell] ~/d/m/s/s/releng_frontend % exit

'''.format(
    apps=''.join([' - ' + i + '\n' for i in please_cli.config.APPS]),
)


@click.command(
    cls=please_cli.utils.ClickCustomCommand,
    short_help="Enter development environment of an APPLICATION.",
    epilog="Happy hacking!",
    help=CMD_HELP,
    )
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
    )
@click.option(
    '--zsh',
    is_flag=True,
    help='Run in zsh',
    )
@click.option(
    '--nix-shell',
    required=True,
    default=please_cli.config.NIX_BIN_DIR + 'nix-shell',
    help='Path to nix-shell command (default: {}).'.format(
        please_cli.config.NIX_BIN_DIR + 'nix-shell',
        ),
    )
def cmd(app, zsh, nix_shell):
    command = '{nix_shell} {default_nix} -A {app} {zsh}'.format(
        app=app,
        nix_shell=nix_shell,
        default_nix=os.path.join(
            please_cli.config.ROOT_DIR, 'nix/default.nix'),
        zsh=zsh and '--run zsh' or '',
    )

    os.environ['SERVICES_ROOT'] = please_cli.config.ROOT_DIR + '/'

    log.debug('Running command using os.system', command=command)
    os.system(command)


if __name__ == "__main__":
    cmd()
