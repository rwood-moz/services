# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os

import click
import click_spinner

import please_cli.config
import please_cli.utils
import please_cli.shell


CMD_HELP = '''
Run tests, linters, etc.. for an APPLICATION.

\b
APPLICATIONS:
{apps}

'''.format(
    apps=''.join([' - ' + i + '\n' for i in please_cli.config.APPS]),
)


def check_result(returncode, output):
    if returncode == 0:
        click.secho('SUCCESS', fg='green')
    else:
        click.secho('ERROR', fg='red')

    if returncode != 0:
        show_details = click.confirm(
            'Show details?', default=False, abort=False, prompt_suffix=' ',
            show_default=True, err=False)
        if show_details:
            click.echo_via_pager(output)


@click.command(
    cls=please_cli.utils.ClickCustomCommand,
    short_help="Run tests, linters, etc.. for an APPLICATION.",
    epilog="Happy hacking!",
    help=CMD_HELP,
    )
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
    )
@click.pass_context
def cmd(ctx, app):
    checks = please_cli.config.APPS.get(app, {}).get('checks')

    if not checks:
        raise click.ClickException('No checks found for `{}` application.'.format(app))

    click.echo('Checking:')
    for check_title, check_command in checks:
        click.echo(' => {}: '.format(check_title), nl=False)
        with click_spinner.spinner():
            returncode, output, error = ctx.invoke(please_cli.shell.cmd,
                                                   app=app,
                                                   quiet=True,
                                                   command=check_command,
                                                   )
        check_result(returncode, output)


if __name__ == "__main__":
    cmd()

