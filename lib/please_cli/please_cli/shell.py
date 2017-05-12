# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import click
import os

import please_cli.config


@click.command()
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
    )
@click.option(
    '--nix-shell',
    required=True,
    default=please_cli.config.NIX_BIN_DIR + 'nix-shell',
    help='`nix-shell` command',
    )
def cmd(app, nix_shell):
    os.system('{nix_shell} {default_nix} -A {app}'.format(
        app=app,
        nix_shell=nix_shell,
        default_nix=os.path.join(
            please_cli.config.ROOT_DIR, 'nix/default.nix'),
    ))


if __name__ == "__main__":
    cmd()
