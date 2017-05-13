# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import shlex
import click
import subprocess
import cli_common.log


log = cli_common.log.get_logger('please-cli.utils')


class ClickCustomCommand(click.Command):
    """A custom click command which doesn't indent help and epilog text.
    """

    def format_help_text(self, ctx, formatter):
        """Writes the help text to the formatter if it exists."""
        if self.help:
            formatter.write_paragraph()
            formatter.write_text(self.help)

    def format_epilog(self, ctx, formatter):
        """Writes the epilog into the formatter if it exists."""
        if self.epilog:
            formatter.write_paragraph()
            formatter.write_text(self.epilog)

    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)

        if opts:
            with formatter.section('OPTIONS'):
                formatter.write_dl(opts)



class ClickCustomGroup(click.Group, ClickCustomCommand):
    """A custom click group Command which doesn't indent help and epilog text.
    """

    def format_options(self, ctx, formatter):
        ClickCustomCommand.format_options(self, ctx, formatter)
        self.format_commands(ctx, formatter)

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        rows = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if getattr(cmd, 'hidden', None):
                continue

            help = cmd.short_help or ''
            rows.append((subcommand, help))

        if rows:
            with formatter.section('COMMANDS'):
                formatter.write_dl(rows)
