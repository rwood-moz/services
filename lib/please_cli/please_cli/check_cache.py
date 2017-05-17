# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os
import subprocess

import click
import click_spinner
import requests

import cli_common.command
import cli_common.log

import please_cli.config
import please_cli.utils


log = cli_common.log.get_logger(__name__)


class Derive:
    def __init__(self, *drv):
        self._drv = drv

    @property
    def nix_hash(self):
        return self._drv[0][0][1][11:43]


@click.command()
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
    )
@click.option(
    '--cache-url',
    required=True,
    default=please_cli.config.CACHE_URL,
    help='Location of builartifacts.',
    )
@click.option(
    '--nix-instantiate',
    required=True,
    default='nix-instantiate',
    help='`nix-instantiate` command',
    )
def cmd(app, cache_url, nix_instantiate, indent=0, interactive=True):
    """Command to check if application is already in cache.
    """

    indent = ' ' * indent

    click.echo('{} => Calculating `{}` hash ... '.format(indent, app), nl=False)
    command = [
        nix_instantiate,
        os.path.join(please_cli.config.ROOT_DIR, 'nix/default.nix'),
        '-A', app
    ]
    if interactive:
        with click_spinner.spinner():
            result, output, error = cli_common.command.run(
                command,
                stream=True,
                stderr=subprocess.STDOUT,
            )
    else:
        result, output, error = cli_common.command.run(
            command,
            stream=True,
            stderr=subprocess.STDOUT,
        )
    please_cli.utils.check_result(
        result,
        output,
        ask_for_details=interactive,
    )

    try:
        drv = output.split('\n')[-1].strip()
        with open(drv) as f:
            derivation = eval(f.read())
    except Exception as e:
        log.exception(e)
        raise click.ClickException('Something went wrong when reading derivation file for `{}` application.'.format(app))
    click.echo('{}    Application hash: {}'.format(indent, derivation.nix_hash))

    click.echo('{} => Checking cache if build artifacts exists for `{}` ... '.format(indent, app), nl=False)
    with click_spinner.spinner():
        response = requests.get(
            '%s/%s.narinfo' % (cache_url, derivation.nix_hash),
        )

    app_exists = response.status_code == 200

    please_cli.utils.check_result(
        app_exists and 0 or 1,
        success_message='EXISTS',
        error_message='NOT EXISTS',
        raise_exception=False,
        ask_for_details=False,
    )

    return app_exists, derivation.nix_hash


if __name__ == "__main__":
    cmd()
