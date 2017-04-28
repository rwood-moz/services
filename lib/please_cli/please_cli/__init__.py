# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import sys
import click
import cli_common.log

excepthook = sys.excepthook
sys.excepthook = lambda et, e, t: click.echo("ERROR: " + str(e))  # noqa

import please_cli.build
import please_cli.check_cache
import please_cli.deploy
import please_cli.github
import please_cli.maintanance
import please_cli.utils


@click.group("please")
@click.option('-D', '--debug', is_flag=True, help="TODO: add description")
@click.option('--mozdef', type=str, default=None, help="TODO: add description")
@click.pass_context
def cmd(ctx, debug, mozdef):
    """TODO: add description
    """

    cli_common.log.init_logger(debug, mozdef)

    if debug is True:
        sys.excepthook = excepthook

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


cmd.add_command(please_cli.check_cache.cmd, "check-cache")
cmd.add_command(please_cli.github.cmd, "github")
cmd.add_command(please_cli.build.cmd, "build")
# TODO: cmd.add_command(please_cli.deploy.cmd, "deploy")
cmd.add_command(please_cli.deploy.cmd_S3, "deploy:S3")
cmd.add_command(please_cli.deploy.cmd_HEROKU, "deploy:heroku")
cmd.add_command(please_cli.maintanance.cmd_on, "maintanance:on")
cmd.add_command(please_cli.maintanance.cmd_off, "maintanance:off")


if __name__ == "__main__":
    cmd()
