# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os
import click
import awscli.clidriver

import cli_common.taskcluster

import please_cli.config
import please_cli.utils


@click.command()
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
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
    '--cache-access-key-id',
    required=False,
    default=None,
    )
@click.option(
    '--cache-secret-access-key',
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
        nix_build,
        nix_push,
        cache_bucket,
        cache_access_key_id,
        cache_secret_access_key,
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

        # TODO: check below secrets and error if they dont exits
        AWS_ACCESS_KEY_ID = secrets['CACHE_ACCESS_KEY_ID']
        AWS_SECRET_ACCESS_KEY = secrets['CACHE_SECRET_ACCESS_KEY']

    if app in ['releng-frontend', 'releng-docs', 'shipit-frontend']:
        code, output =  please_cli.utils.run_command(
            '{nix_build} {ROOT_DIR}/nix/default.nix -A apps.{app} -o {ROOT_DIR}/result-{app}'.format(  # noqa
                app=app,
                nix_build=nix_build,
                ROOT_DIR=please_cli.config.ROOT_DIR,
                ))
    else:
        code, output =  please_cli.utils.run_command(
            '{nix_build} {ROOT_DIR}/nix/default.nix -A apps.{app}.docker -o {ROOT_DIR}/result-{app}'.format(  # noqa
                app=app,
                nix_build=nix_build,
                ROOT_DIR=please_cli.config.ROOT_DIR,
                ))
    # TODO: report errors correctly
    # TODO: also build hooks / docker images

    if cache_bucket:
        tmp_cache_dir = os.path.join(please_cli.config.TMP_DIR, 'cache')
        outputs = ' '.join([
            item
            for item in os.listdir(please_cli.config.ROOT_DIR)
            if item.startswith('result-')
        ])

        if not os.path.exists(tmp_cache_dir):
            os.makedirs(tmp_cache_dir)

        code, output =  please_cli.utils.run_command(
            '{nix_push} --dest {tmp_cache_dir} --force {outputs}'.format(  # noqa
                nix_push=nix_push,
                tmp_cache_dir=tmp_cache_dir,
                outputs=outputs,
                ))
        # TODO: report errors correctly

        os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
        os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
        aws = awscli.clidriver.create_clidriver().main
        result = aws([
            's3',
            'sync',
            '--size-only',
            '--acl', 'public-read',
            tmp_cache_dir,
            's3://' + cache_bucket,
        ])
        # TODO: handle result (should be 0)


if __name__ == "__main__":
    cmd()
