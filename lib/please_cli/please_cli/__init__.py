# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import click
import logbook
import cli_common.log

import please_cli.build
import please_cli.build_base_image
import please_cli.check
import please_cli.check_cache
import please_cli.create_certs
import please_cli.deploy
import please_cli.github
import please_cli.maintanance
import please_cli.nixify
import please_cli.run
import please_cli.shell
import please_cli.utils


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

\b
APPLICATIONS:
{apps}

'''.format(
    apps=''.join([' - ' + i + '\n' for i in please_cli.config.APPS]),
)

CMD_EPILOG = '''
For tools information look at:

  https://docs.mozilla-releng.net

Happy hacking!
'''.format(
)


@click.group("please", cls=please_cli.utils.ClickCustomGroup,
             invoke_without_command=True, help=CMD_HELP, epilog=CMD_EPILOG)
@click.option('-v', '--verbose', count=True, help='Increase verbosity level')
@click.version_option(version=please_cli.config.VERSION)
@click.help_option()
@click.option('--mozdef', type=str, default=None, help="TODO: add description")
@click.pass_context
def cmd(ctx, verbose, mozdef):

    # critical – for errors that lead to termination
    log_level = logbook.CRITICAL

    # error – for errors that occur, but are handled
    if verbose == 1:
        log_level = logbook.ERROR

    # warning – for exceptional circumstances that might not be errors
    elif verbose == 2:
        log_level = logbook.WARNING

    # notice – for non-error messages you usually want to see
    elif verbose == 3:
        log_level = logbook.NOTICE

    # info – for messages you usually don’t want to see
    elif verbose == 4:
        log_level = logbook.INFO

    # debug – for debug messages
    elif verbose >= 5:
        log_level = logbook.DEBUG

    cli_common.log.init_logger(log_level, mozdef)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


cmd.add_command(please_cli.check.cmd, "check")
cmd.add_command(please_cli.run.cmd, "run")
cmd.add_command(please_cli.shell.cmd, "shell")


@click.group()
@click.pass_context
def cmd_tools(ctx):
    """Different tools and helping utilities.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


cmd.add_command(cmd_tools, "tools")
cmd_tools.add_command(please_cli.build.cmd, "build")
cmd_tools.add_command(please_cli.check_cache.cmd, "check-cache")
cmd_tools.add_command(please_cli.create_certs.cmd, "create-certs")
cmd_tools.add_command(please_cli.deploy.cmd_HEROKU, "deploy:HEROKU")
cmd_tools.add_command(please_cli.deploy.cmd_S3, "deploy:S3")
cmd_tools.add_command(please_cli.deploy.cmd_TASKCLUSTER_HOOK, "deploy:TASKCLUSTER_HOOK")
cmd_tools.add_command(please_cli.github.cmd, "github")
cmd_tools.add_command(please_cli.maintanance.cmd_off, "maintanance:off")
cmd_tools.add_command(please_cli.maintanance.cmd_on, "maintanance:on")
cmd_tools.add_command(please_cli.nixify.cmd, "nixify")
cmd_tools.add_command(please_cli.build_base_image.cmd, "build-base-image")


if __name__ == "__main__":
    cmd()
