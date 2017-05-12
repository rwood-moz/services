# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import awscli
import click
import io
import os
import push.image
import push.registry
import shutil
import taskcluster
import tempfile

import cli_common
import please_cli.config
import please_cli.build



@click.command()
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
    )
@click.argument(
    's3_bucket',
    required=True,
    )
@click.option(
    '--csp',
    required=False,
    default=None,
    )
@click.option(
    '--flags',
    required=False,
    default=None,
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
@click.pass_context
def cmd_S3(ctx,
           app,
           s3_bucket,
           csp,
           flags,
           nix_build,
           nix_push,
           taskcluster_secrets,
           taskcluster_client_id,
           taskcluster_access_token,
           ):
    '''
    '''

    taskcluster = cli_common.taskcluster.TaskclusterClient(
        taskcluster_client_id,
        taskcluster_access_token,
    )
    secrets_tool = taskcluster.get_service('secrets')
    secrets = secrets_tool.get(taskcluster_secrets)['secret']

    # TODO: we need to change this
    AWS_ACCESS_KEY_ID = secrets['DEPLOY_S3_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = secrets['DEPLOY_S3_SECRET_ACCESS_KEY']

    # 1. build app (but only pull from cache)
    ctx.invoke(please_cli.build.cmd,
               app=app,
               nix_build=nix_build,
               nix_push=nix_push,
               taskcluster_secrets=taskcluster_secrets,
               taskcluster_client_id=taskcluster_client_id,
               taskcluster_access_token=taskcluster_access_token,
               )
    app_path = os.path.realpath(os.path.join(
        please_cli.config.ROOT_DIR,
        "result-" + app,
    ))

    # 2. create temporary copy of app
    if not os.path.exists(please_cli.config.TMP_DIR):
        os.makedirs(please_cli.config.TMP_DIR)
    tmp_dir = tempfile.mkdtemp(
        prefix='copy-of-result-{}-'.format(app),
        dir=please_cli.config.TMP_DIR,
    )
    shutil.rmtree(tmp_dir)
    shutil.copytree(app_path, tmp_dir, copy_function=shutil.copy)

    # 3. apply csp and flags to index.html
    index_html_file = os.path.join(tmp_dir, 'index.html')
    with io.open(index_html_file, 'r', encoding='utf-8') as f:
        index_html = f.read()

    if csp:
        index_html = index_html.replace(
            'font-src \'self\';',
            'font-src \'self\'; connect-src {};'.format(csp),
        )
    if flags:
        index_html = index_html.replace(
            '<body',
            '<body ' + flags,
        )

    os.chmod(index_html_file, 755)
    with io.open(index_html_file, 'w', encoding='utf-8') as f:
        f.write(index_html)

    # 4. sync to S3
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    aws = awscli.clidriver.create_clidriver().main
    aws([
        's3',
        'sync',
        '--delete',
        '--acl', 'public-read',
        tmp_dir,
        's3://' + s3_bucket,
    ])



@click.command()
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
    )
@click.argument(
    'heroku_app',
    required=True,
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
@click.pass_context
def cmd_HEROKU(ctx,
               app,
               heroku_app,
               nix_build,
               nix_push,
               taskcluster_secrets,
               taskcluster_client_id,
               taskcluster_access_token,
               ):

    taskcluster = cli_common.taskcluster.TaskclusterClient(
        taskcluster_client_id,
        taskcluster_access_token,
    )
    secrets_tool = taskcluster.get_service('secrets')
    secrets = secrets_tool.get(taskcluster_secrets)['secret']

    HEROKU_USERNAME = secrets['HEROKU_USERNAME']
    HEROKU_PASSWORD = secrets['HEROKU_PASSWORD']

    ctx.invoke(please_cli.build.cmd,
               app=app,
               nix_build=nix_build,
               nix_push=nix_push,
               taskcluster_secrets=taskcluster_secrets,
               taskcluster_client_id=taskcluster_client_id,
               taskcluster_access_token=taskcluster_access_token,
               )

    app_path = os.path.realpath(os.path.join(
        please_cli.config.ROOT_DIR,
        "result-" + app,
    ))

    push.registry.push(
        push.image.spec(app_path),
        "https://registry.heroku.com",
        HEROKU_USERNAME,
        HEROKU_PASSWORD,
        heroku_app + "/web",
        "latest",
    )


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
@click.pass_context
def cmd_TASKCLUSTER_HOOK(ctx,
                         app,
                         nix_build,
                         nix_push,
                         taskcluster_secrets,
                         taskcluster_client_id,
                         taskcluster_access_token,
                         ):
    click.echo("TODO")
    # taskcluster-hooks.json: require-APP require-BRANCH nix
    # 	@nix-build nix/taskcluster_hooks.nix \
    # 		--argstr app "$(APP)" \
    # 		--argstr branch "$(BRANCH)" \
    # 		-o result-taskcluster-hooks.json --fallback
    # 
    # taskcluster-hooks: taskcluster-hooks.json require-APP require-BRANCH require-DOCKER require-HOOKS_URL build-tool-push build-tool-taskcluster-hooks
    # 	@./result-tool-taskcluster-hooks/bin/taskcluster-hooks \
    # 		--hooks=./result-taskcluster-hooks.json \
    #         --hooks-group=project-releng \
    #         --hooks-prefix=services-$(BRANCH)-$(APP)- \
    #         --hooks-url=$(HOOKS_URL) \
    #         --docker-push=./result-tool-push/bin/push \
    # 		--docker-registry=https://index.docker.io \
    #         --docker-repo=garbas/releng-services \
    #         --docker-username=$(DOCKER_USERNAME) \
    #         --docker-password=$(DOCKER_PASSWORD)
    # 
    # taskcluster-hooks-manual: taskcluster-hooks.json require-APP require-BRANCH require-DOCKER require-HOOKS_CREDS build-tool-push build-tool-taskcluster-hooks
    # 	@./result-tool-taskcluster-hooks/bin/taskcluster-hooks \
    # 		--hooks=./result-taskcluster-hooks.json \
    #         --hooks-group=project-releng \
    #         --hooks-prefix=services-$(BRANCH)-$(APP)- \
    #         --hooks-client-id=$(HOOKS_CLIENT_ID) \
    #         --hooks-access-token=$(HOOKS_ACCESS_TOKEN) \
    #         --docker-push=./result-tool-push/bin/push \
    # 		--docker-registry=https://index.docker.io \
    #         --docker-repo=garbas/releng-services \
    #         --docker-username=$(DOCKER_USERNAME) \
    #         --docker-password=$(DOCKER_PASSWORD)
