# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import click
import os

import cli_common.log
import please_cli.config


log = cli_common.log.get_logger(__name__)


@click.command()
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
    help='`nix-shell` command',
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
