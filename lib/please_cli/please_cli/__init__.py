# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import sys

import click
import cli_common.log

import please_cli.build
import please_cli.check
import please_cli.check_cache
import please_cli.create_certs
import please_cli.deploy
import please_cli.github
import please_cli.initdb
import please_cli.maintanance
import please_cli.nixify
import please_cli.run
import please_cli.shell
import please_cli.utils

#excepthook = sys.excepthook
#sys.excepthook = lambda et, e, t: click.echo("ERROR: " + str(e))  # noqa


CMD_HELP = '''

Welcome to `please` command line utility which should help you develop
`mozilla-releng/services` applications.

To enter a development shell of application do:

  % ./please shell <APPLICATION>

To run application in a foreground mode do:

  % ./please run <APPLICATION>

To run tests, linters, etc... do:

  % ./please check <APPLICATION>

Above is usefull to run before pushing code to upstream repository.

'''.format(
)

CMD_EPILOG = '''
\b
APPLICATIONS:
{apps}

For more information look at:

  https://docs.mozilla-releng.net

Happy hacking!
'''.format(
    apps=''.join([' - ' + i + '\n' for i in please_cli.config.APPS]),
)


@click.group("please", cls=please_cli.utils.ClickCustomGroup,
             invoke_without_command=True, help=CMD_HELP, epilog=CMD_EPILOG)
@click.option('-D', '--debug', is_flag=True, help="TODO: add description")
@click.version_option(version=please_cli.config.VERSION)
@click.help_option()
@click.option('--mozdef', type=str, default=None, help="TODO: add description")
@click.pass_context
def cmd(ctx, debug, mozdef):

    cli_common.log.init_logger(debug, mozdef)

    if debug is True:
        sys.excepthook = excepthook

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


cmd.add_command(please_cli.check.cmd, "check")
cmd.add_command(please_cli.run.cmd, "run")
cmd.add_command(please_cli.shell.cmd, "shell")


@click.group("more")
@click.pass_context
def cmd_more(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


cmd.add_command(cmd_more, "show-more")
cmd_more.add_command(please_cli.check_cache.cmd, "check-cache")
cmd_more.add_command(please_cli.create_certs.cmd, "create-certs")
cmd_more.add_command(please_cli.initdb.cmd, "initdb")
cmd_more.add_command(please_cli.deploy.cmd_HEROKU, "deploy:heroku")
cmd_more.add_command(please_cli.deploy.cmd_S3, "deploy:S3")
cmd_more.add_command(please_cli.deploy.cmd_TASKCLUSTER_HOOK, "deploy:hook")
cmd_more.add_command(please_cli.github.cmd, "github")
cmd_more.add_command(please_cli.maintanance.cmd_off, "maintanance:off")
cmd_more.add_command(please_cli.maintanance.cmd_on, "maintanance:on")
cmd_more.add_command(please_cli.nixify.cmd, "nixify")
cmd_more.add_command(please_cli.build.cmd, "build")


if __name__ == "__main__":
    cmd()
