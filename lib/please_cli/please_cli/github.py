# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import cli_common.taskcluster
import click
import datetime
import json
import os
import please_cli.config
import slugid


def get_build_task(index,
                   app,
                   task_group_id,
                   parent_task,
                   github_commit,
                   github_branch,
                   github_user_email,
                   ):
    command = (' && '.join([
      'cd /tmp',
      'wget https://github.com/mozilla-releng/services/archive/{github_commit}.tar.gz',  # noqa
      'tar zxf {github_commit}.tar.gz',
      'cd services-{github_commit}',
      'env',
      './please -D build'
        ' --cache-bucket="releng-cache"'
        ' --taskcluster-secrets=repo:github.com/mozilla-releng/services:branch:{github_branch}'  # noqa
        ' {app}'
    ])).format(
        github_branch=github_branch,
        github_commit=github_commit,
        app=app,
    )
    return get_task(
        task_group_id,
        [ parent_task ],
        github_commit,
        github_branch,
        command,
        {
            'name': '1.{index:02}. Building {app}'.format(
                index=index + 1,
                app=app,
            ),
            'description': '',
            'owner': github_user_email,
            'source': 'https://github.com/mozilla-releng/services/tree/' + github_branch,

        },
    )


def get_deploy_task(index,
                    app,
                    app_config,
                    task_group_id,
                    parent_task,
                    github_commit,
                    github_branch,
                    github_user_email,
                    ):

    # XXX: we need to offload this to 
    if app in ['releng-frontend', 'releng-docs', 'shipit-frontend']:
        please_command = './please -D deploy:S3 "{app}" "{s3_bucket}" --csp="{csp}" --flags="${flags}" --taskcluster-secrets="{taskcluster_secrets}"'.format(
            app=app,
            s3_bucket=app_config['s3_bucket'],
            csp=' '.join(app_config.get('csp', [])),
            flags=' '.join([
                '--data-{}="{}"'.format(k, v)
                for k, v in app_config.get('flags', dict()).items()
            ]),
            taskcluster_secrets='repo:github.com/mozilla-releng/services:branch:' + github_branch,
        )
    else:
        please_command = './please -D deploy:heroku "{app}" "{heroku_app}" --taskcluster-secrets="{taskcluster_secrets}"'.format(
            app=app,
            heroku_app=app_config['heroku_app'],
            taskcluster_secrets='repo:github.com/mozilla-releng/services:branch:' + github_branch,
        )

    command = (' && '.join([
      'cd /tmp',
      'wget https://github.com/mozilla-releng/services/archive/{github_commit}.tar.gz',  # noqa
      'tar zxf {github_commit}.tar.gz',
      'cd services-{github_commit}',
      'env',
       please_command
    ])).format(
        github_commit=github_commit,
    )
    return get_task(
        task_group_id,
        [ parent_task ],
        github_commit,
        github_branch,
        command,
        {
            'name': '3.{index:02}. Deploying {app}'.format(
                index=index + 1,
                app=app,
            ),
            'description': '',
            'owner': github_user_email,
            'source': 'https://github.com/mozilla-releng/services/tree/' + github_branch,

        },
    )


def get_task(task_group_id,
             dependencies,
             github_commit,
             github_branch,
             command,
             metadata,
             deadline=dict(hours=5),
             ):
    now = datetime.datetime.utcnow()
    return {
        'provisionerId': 'aws-provisioner-v1',
        'workerType': 'releng-task',
        'schedulerId': 'taskcluster-github',
        'taskGroupId': task_group_id,
        'dependencies': dependencies,
        'created': now,
        'deadline': now + datetime.timedelta(**deadline),
        'scopes': [
          'secrets:get:repo:github.com/mozilla-releng/services:branch:' + github_branch,
        ],
        'payload': {
            'maxRunTime': 7200,  # seconds (i.e. two hours)
            'image': 'garbas/mozilla-releng-services:base-latest',
            'features': {
                'taskclusterProxy': True,
            },
            'command': [
                '/bin/bash',
                '-c',
                command,
            ],
        },
        'metadata': metadata,
    }


@click.command()
@click.option(
    '--github-commit',
    envvar="GITHUB_HEAD_SHA",
    required=True,
    )
@click.option(
    '--github-branch',
    envvar="GITHUB_HEAD_BRANCH",
    required=True,
    )
@click.option(
    '--github-user-email',
    envvar="GITHUB_HEAD_USER_EMAIL",
    required=True,
    )
@click.option(
    '--task-id',
    envvar="TASK_ID",
    required=True,
    )
@click.option(
    '--cache-url',
    required=True,
    default=please_cli.config.CACHE_URL,
    help='Location of build artifacts.',
    )
@click.option(
    '--nix-instantiate',
    required=True,
    default=please_cli.config.NIX_BIN_DIR + 'nix-instantiate',
    help='`nix-instantiate` command',
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
@click.option(
    '--dry-run',
    is_flag=True,
    )
def cmd(github_commit,
        github_branch,
        github_user_email,
        task_id,
        cache_url,
        nix_instantiate,
        taskcluster_client_id,
        taskcluster_access_token,
        dry_run,
        ):
    """A tool to be ran on each commit.
    """

    taskcluster = cli_common.taskcluster.TaskclusterClient(
        taskcluster_client_id,
        taskcluster_access_token,
    )
    taskcluster_secrets = taskcluster.get_service('secrets')
    taskcluster_queue = taskcluster.get_service('queue')
    taskcluster_index = taskcluster.get_service('index')

    click.echo("1/5: Retriving current taskGroupId")

    task = taskcluster_queue.task(task_id)
    task_group_id = task['taskGroupId']

    click.echo("2/5: Retriving secrets")

    secrets_id = 'repo:github.com/mozilla-releng/services:branch:' + github_branch  # noqa
    secrets = taskcluster_secrets.get(secrets_id)['secret']

    click.echo('3/5: Checking cache which application needs to be built and which deployed')

    build_apps = []
    app_hashes = dict()
    for app in please_cli.config.APPS:
        click.echo(' => ' + app + ': ', nl=False) 
        if dry_run:
            app_exists_in_cache, app_hash = False, "EEEE"
        else:
            app_exists_in_cache, app_hash = please_cli.check_cache.app_exists(
                app, cache_url, nix_instantiate)
        app_hashes[app] = app_hash
        if not app_exists_in_cache:
            build_apps.append(app)
            click.echo('DOES NOT EXISTS!')
        else:
            click.echo('EXISTS!')

    # calculate which apps we need to deploy
    deploy_apps = []
    if github_branch in please_cli.config.DEPLOYMENT_BRANCHES:

        # TODO: get status for our index branch
        status = dict()

        for app in please_cli.config.APPS:
            app_hash = status.get(app)

            if app_hash == app_hashes[app]:
                continue

            deploy_apps.append(app)
        
    click.echo('4/5: Creating taskcluster tasks definitions')
    tasks = []

    # 1. build tasks
    build_tasks = {}
    for index, app in enumerate(build_apps):
        app_uuid = slugid.nice().decode('utf-8')
        build_tasks[app_uuid] = get_build_task(
            index,
            app,
            task_group_id,
            task_id,
            github_commit,
            github_branch,
            github_user_email,
        )
        tasks.append((app_uuid, build_tasks[app_uuid]))

    if deploy_apps:

        # 2. maintanance on task
        maintanance_on_uuid = slugid.nice().decode('utf-8')
        if len(build_tasks.keys()) == 0:
            maintanance_on_dependencies = [ task_id ]
        else:
            maintanance_on_dependencies = [i for i in build_tasks.keys()]
        maintanance_on_command = (' && '.join([
          'cd /tmp',
          'wget https://github.com/mozilla-releng/services/archive/{github_commit}.tar.gz',  # noqa
          'tar zxf {github_commit}.tar.gz',
          'cd services-{github_commit}',
          'env',
          './please -D maintanance:on {apps}',
        ])).format(
            github_commit=github_commit,
            apps=' '.join(build_apps),
        )
        maintanance_on_task = get_task(
            task_group_id,
            maintanance_on_dependencies,
            github_commit,
            github_branch,
            maintanance_on_command,
            {
                'name': '2. Maintanance ON',
                'description': '',
                'owner': github_user_email,
                'source': 'https://github.com/mozilla-releng/services/tree/' + github_branch,

            },
        )
        tasks.append((maintanance_on_uuid, maintanance_on_task))

        # 3. deploy tasks (if on production/staging)
        deploy_tasks = {}
        if github_branch == 'production':
            apps_config = please_cli.config.DEPLOY_PRODUCTION
        else:
            apps_config = please_cli.config.DEPLOY_STAGING
        index = 0
        for app in deploy_apps:
            if app not in apps_config:
                continue
            app_uuid = slugid.nice().decode('utf-8')
            deploy_tasks[app_uuid] = get_deploy_task(
                index,
                app,
                apps_config[app],
                task_group_id,
                maintanance_on_uuid,
                github_commit,
                github_branch,
                github_user_email,
            )
            tasks.append((app_uuid, deploy_tasks[app_uuid]))
            index += 1

        # 4. maintanance off task
        maintanance_off_uuid = slugid.nice().decode('utf-8')
        maintanance_off_command = (' && '.join([
          'cd /tmp',
          'wget https://github.com/mozilla-releng/services/archive/{github_commit}.tar.gz',  # noqa
          'tar zxf {github_commit}.tar.gz',
          'cd services-{github_commit}',
          'env',
          './please -D maintanance:off {apps}',
        ])).format(
            github_commit=github_commit,
            apps=' '.join(build_apps),
        )
        maintanance_off_task = get_task(
            task_group_id,
            [i for i in deploy_tasks.keys()],
            github_commit,
            github_branch,
            maintanance_off_command,
            {
                'name': '4. Maintanance OFF',
                'description': '',
                'owner': github_user_email,
                'source': 'https://github.com/mozilla-releng/services/tree/' + github_branch,

            },
        )
        maintanance_off_task['requires'] = 'all-resolved'
        tasks.append((maintanance_off_uuid, maintanance_off_task))

    click.echo('5/5: Submitting taskcluster definitions to taskcluster')
    if dry_run:
        tasks2 = {task_id: task for task_id, task in tasks}
        for task_id, task in tasks:
            click.echo(' => %s (%s)' % (task['metadata']['name'], task_id))
            click.echo('    dependencies:')
            for dep in task['dependencies']:
                depName = "0. Decision task"
                if dep in tasks2:
                    depName = tasks2[dep]['metadata']['name']
                click.echo('      - %s (%s)' % (depName, dep))
    else:
        for task_id, task in tasks:
            taskcluster_queue.createTask(task_id, task)


if __name__ == "__main__":
    cmd()
