# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import logging

from shipit_pipeline.pipeline import get_runnable_steps, get_running_steps, refresh_pipeline_steps, start_steps,\
    PipelineStep

log = logging.getLogger(__name__)

PIPELINES = {

}


def list_pipelines():
    log.info('listing pipelines')
    return list(PIPELINES.keys())


def get_pipeline(uid):
    log.info('getting pipeline %s', uid)
    try:
        return PIPELINES[uid][1]
    except (KeyError, ValueError):
        return None, 404


def get_pipeline_status(uid):
    log.info('getting pipeline status %s', uid)
    return dict(
        state=PIPELINES[uid][0]
    )


def create_pipeline(uid, pipeline):
    log.info('creating pipeline %s', uid)
    pipeline_steps = [PipelineStep.from_dict(step) for step in pipeline['parameters']['steps']]
    PIPELINES[uid] = ['running', pipeline_steps]


def delete_pipeline(uid):
    log.info('deleting pipeline %s', uid)
    del PIPELINES[uid]


def update_pipeline_state(uid, state):
    PIPELINES[uid][0] = state


def ticktock():

    try:
        print('In ticktock')
        running_pipelines = [
            (uid, status, steps) for (uid, (status, steps)) in PIPELINES.items() if status == 'running'
        ]

        print('running_pipelines', running_pipelines)
        for uid, status, steps in running_pipelines:
            refreshed_steps = refresh_pipeline_steps(steps)
            print('refreshed_steps', refreshed_steps)
            runnables = get_runnable_steps(refreshed_steps)
            running = get_running_steps(refreshed_steps)

            if len(runnables) == 0 and len(running) == 0:
                update_pipeline_state(uid, state='finished')     # May be not a success
                print('Pipeline "{}" finished'.format(uid))

            elif runnables:
                start_steps(runnables)
                print('Started', runnables)

            else:
                print('Nothing starts but things are running')
    except Exception as e:
        import traceback
        print('OH NOES!', e)
        traceback.print_exc()
