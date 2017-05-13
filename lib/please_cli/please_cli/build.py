# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os
import subprocess

import awscli.clidriver
import click
import click_spinner
import colorama

import cli_common.log
import cli_common.taskcluster
import cli_common.command

import please_cli.config


log = cli_common.log.get_logger(__name__)


def check_result(returncode):
    if returncode == 0:
        click.secho('\bDONE', fg='green')
    else:
        click.secho('\bERROR', fg='green')
        raise click.ClickException('Please consult the logs for error.')


@click.command()
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
    )
@click.option(
    '--to-deploy',
    is_flag=True,
    )
@click.option(
    '--nix-build',
    required=True,
    default=please_cli.config.NIX_BIN_DIR + 'nix-build',
    help='`nix-build` command',
    )
@click.option(
    '--nix-push',
    required=True,
    default=please_cli.config.NIX_BIN_DIR + 'nix-push',
    help='`nix-push` command',
    )
@click.option(
    '--cache-bucket',
    required=False,
    default=None,
    )
@click.option(
    '--taskcluster-secrets',
    required=True,
    )
@click.option(
    '--taskcluster-client-id',
    default=None,
    required=False,
    )
@click.option(
    '--taskcluster-access-token',
    default=None,
    required=False,
    )
def cmd(app,
        to_deploy,
        nix_build,
        nix_push,
        cache_bucket,
        taskcluster_secrets,
        taskcluster_client_id,
        taskcluster_access_token,
        ):

    secrets = dict()

    if cache_bucket:
        taskcluster = cli_common.taskcluster.TaskclusterClient(
            taskcluster_client_id,
            taskcluster_access_token,
        )
        secrets_tool = taskcluster.get_service('secrets')
        secrets = secrets_tool.get(taskcluster_secrets)['secret']

        AWS_ACCESS_KEY_ID = secrets.get('CACHE_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = secrets.get('CACHE_SECRET_ACCESS_KEY')

        if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None:
            raise click.UsageError(click.wrap_text(
                'ERROR: CACHE_ACCESS_KEY_ID and/or CACHE_SECRET_ACCESS_KEY '
                'are not in Taskcluster secret (`{}`).'.format(taskcluster_secrets)
            ))

    command = [
        nix_build,
        please_cli.config.ROOT_DIR + '/nix/default.nix',
        '-A', app + (to_deploy and '.deploy' or ''),
        '-o', please_cli.config.ROOT_DIR + '/result-' + app,
    ]

    click.echo('Building {} ... '.format(app), nl=False)
    with click_spinner.spinner():
        result, output, error = cli_common.command.run(
            command,
            stream=True,
            stderr=subprocess.STDOUT,
        )
        check_result(result)

    if cache_bucket:
        tmp_cache_dir = os.path.join(please_cli.config.TMP_DIR, 'cache')
        outputs = ' '.join([
            os.path.join(please_cli.config.ROOT_DIR, item)
            for item in os.listdir(please_cli.config.ROOT_DIR)
            if item.startswith('result-' + app)
        ])

        if not os.path.exists(tmp_cache_dir):
            os.makedirs(tmp_cache_dir)

        command = [
            nix_push,
            '--dest', tmp_cache_dir,
            '--force', outputs,
        ]
        click.echo('Building cache ... '.format(app), nl=False)
        with click_spinner.spinner():
            result, output, error =  cli_common.command.run(
                command,
                stream=True,
                stderr=subprocess.STDOUT,
            )
            check_result(result)

        os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
        os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
        aws = awscli.clidriver.create_clidriver().main
        click.echo('Pushing cache to S3 ... '.format(app), nl=False)
        with click_spinner.spinner():
            result = aws([
                's3',
                'sync',
                '--quiet',
                '--size-only',
                '--acl', 'public-read',
                tmp_cache_dir,
                's3://' + cache_bucket,
            ])
            check_result(result)


if __name__ == "__main__":
    cmd()
