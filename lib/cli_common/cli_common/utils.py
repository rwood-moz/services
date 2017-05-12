# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import shlex
import subprocess

import cli_common.log


log = cli_common.log.get_logger(__name__)


def run_command(command, **kwargs):
    """
    Run a command through subprocess
    """

    if type(command) is str:
        command_as_string = command
        command = shlex.split(command)
    else:
        command_as_string = ' ' .join(command)

    kwargs = (dict(
        stdin=subprocess.DEVNULL,  # no interactions
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )).update(kwargs)

    log.debug('Running command', command=command_as_string)
    proc = subprocess.Popen(command, **kwargs)

    output, error = proc.communicate()

    if proc.returncode != 0:
        log.critical(
            'Command failed with code: {}'.format(proc.returncode),
            command=command_as_string,
            output=output,
            error=error,
        )
        raise Exception(
            'Command (`{}`) failed with code: {}.'.format(
                command_as_string,
                proc.returncode,
            )
        )

    return output


def run_gecko_command(command, work_dir):
    """
    Run a command through subprocess
    using gecko build environnment
    """
    command = ['gecko-env', ] + command
    return run_command(command, work_dir)
