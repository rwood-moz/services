# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import click
import os

import please_cli.config
import please_cli.utils
import please_cli.build


CMD_HELP = '''
Run tests, linters, etc.. for an APPLICATION.

\b
APPLICATIONS:
{apps}

'''.format(
    apps=''.join([' - ' + i + '\n' for i in please_cli.config.APPS]),
)


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
    ctx.invoke(please_cli.build.cmd, app=app)


if __name__ == "__main__":
    cmd()

