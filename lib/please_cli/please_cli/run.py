# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import click
import os

import please_cli.config


@click.command()
@click.argument(
    'app',
    required=True,
    type=click.Choice(please_cli.config.APPS),
    )
@click.option(
    '--nix-shell',
    required=True,
    default=please_cli.config.NIX_BIN_DIR + 'nix-shell',
    help='`nix-shell` command',
    )
def cmd(app, nix_shell):
    import pdb
    pdb.set_trace()
    # TODO
    #VERSION=$(shell cat VERSION)
    #
    #APP_DEV_DBNAME=services
    #
    #APP_DEV_HOST=localhost
    #
    #APP_DEV_PORT_releng-docs=7000
    #APP_DEV_PORT_frontend-common-example=7001
    #
    #APP_DEV_PORT_releng-frontend=8000
    #APP_DEV_PORT_releng-clobberer=8001
    #APP_DEV_PORT_releng-tooltool=8002
    #APP_DEV_PORT_releng-treestatus=8003
    #APP_DEV_PORT_releng-mapper=8004
    #APP_DEV_PORT_releng-archiver=8005
    #
    #APP_DEV_PORT_shipit-frontend=8010
    #APP_DEV_PORT_shipit-uplift=8011
    #APP_DEV_PORT_shipit-pipeline=8012
    #APP_DEV_PORT_shipit-signoff=8013
    #APP_DEV_PORT_shipit-taskcluster=8014
    #
    #APP_DEV_POSTGRES_PORT=9000
    #
    #APP_DEV=\
    #	WEBPACK_VERSION='v$(VERSION) (devel)' \
    #	WEBPACK_DOCS_URL='http://$(APP_DEV_HOST):$(APP_DEV_PORT_releng-docs)' \
    #	SSL_CACERT=$$PWD/tmp/ca.crt \
    #	SSL_CERT=$$PWD/tmp/server.crt \
    #	SSL_KEY=$$PWD/tmp/server.key
    #APP_DEV_ENV_frontend-common-example=\
    #	$(APP_DEV)
    #APP_DEV_ENV_releng-frontend=\
    #	WEBPACK_DOCS_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_releng-docs) \
    #	WEBPACK_CLOBBERER_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_releng-clobberer) \
    #	WEBPACK_TOOLTOOL_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_releng-tooltool) \
    #	WEBPACK_TREESTATUS_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_releng-treestatus) \
    #	WEBPACK_MAPPER_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_releng-mapper) \
    #	WEBPACK_ARCHIVER_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_releng-archiver) \
    #	$(APP_DEV)
    #APP_DEV_ENV_shipit-frontend=\
    #	WEBPACK_UPLIFT_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_shipit-uplift) \
    #	WEBPACK_PIPELINE_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_shipit-pipeline) \
    #	WEBPACK_BUGZILLA_URL=https://bugzilla-dev.allizom.org \
    #	$(APP_DEV)
    #
    #
    #develop: nix require-APP
    #	@SSL_DEV_CA=$$PWD/tmp nix-shell nix/default.nix -A apps.$(APP)
    #
    #
    #develop-run: require-APP develop-run-$(APP)
    #
    #develop-run-SPHINX : nix require-APP
    #	DEBUG=true \
    #		nix-shell nix/default.nix -A apps.$(APP) \
    #			--run "HOST=$(APP_DEV_HOST) PORT=$(APP_DEV_PORT_$(APP)) python run.py"
    #
    #develop-run-BACKEND: build-certs nix require-APP
    #	$(eval APP_PYTHON=$(subst -,_,$(APP)))
    #	DEBUG=true \
    #	CACHE_TYPE=filesystem \
    #	CACHE_DIR=$$PWD/src/$(APP_PYTHON)/cache \
    #	APP_SETTINGS=$$PWD/src/$(APP_PYTHON)/settings.py \
    #	APP_URL=https://$(APP_DEV_HOST):$(APP_DEV_PORT_$(APP)) \
    #	CORS_ORIGINS="*" \
    #		nix-shell nix/default.nix -A $(APP) \
    #			--run "gunicorn $(APP_PYTHON).flask:app --bind '$(APP_DEV_HOST):$(APP_DEV_PORT_$(APP))' --ca-certs=$$PWD/tmp/ca.crt --certfile=$$PWD/tmp/server.crt --keyfile=$$PWD/tmp/server.key --workers 1 --timeout 3600 --reload --log-file -"
    #
    #develop-run-FRONTEND: build-certs nix require-APP
    #	nix-shell nix/default.nix --pure -A apps.$(APP) \
    #		--run "$(APP_DEV_ENV_$(APP)) webpack-dev-server --host $(APP_DEV_HOST) --port $(APP_DEV_PORT_$(APP)) --config webpack.config.js"
    #
    #develop-run-releng-docs: develop-run-SPHINX
    #develop-run-frontend-common-example: develop-run-FRONTEND
    #
    #develop-run-releng-frontend: develop-run-FRONTEND
    #develop-run-releng-clobberer: require-postgres develop-run-BACKEND
    #develop-run-releng-tooltool: require-postgres develop-run-BACKEND
    #develop-run-releng-treestatus: require-postgres develop-run-BACKEND
    #develop-run-releng-mapper: require-postgres develop-run-BACKEND
    #develop-run-releng-archiver: require-postgres develop-run-BACKEND
    #
    #develop-run-shipit-frontend: develop-run-FRONTEND
    #develop-run-shipit-uplift: require-postgres develop-run-BACKEND
    #develop-run-shipit-pipeline: require-postgres develop-run-BACKEND
    #develop-run-shipit-signoff: require-postgres develop-run-BACKEND
    #develop-run-shipit-taskcluster: require-postgres develop-run-BACKEND
    #
    #develop-run-postgres: build-pkgs-postgresql require-initdb
    #	./result-pkgs-postgresql/bin/postgres -D $(PWD)/tmp/postgres -h localhost -p $(APP_DEV_POSTGRES_PORT)


if __name__ == "__main__":
    cmd()

