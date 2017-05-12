# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import click
import os

import please_cli.config


@click.command()
def cmd(app, nix_shell):
    pass
    # TODO
    #require-initdb: build-pkgs-postgresql
    #        $(eval PG_DATA := $(PWD)/tmp/postgres)
    #        @if [ ! -d $(PG_DATA) ]; then \
    #                ./result-pkgs-postgresql/bin/initdb -D $(PG_DATA) --auth=trust; \
    #        fi

    #require-postgres: build-pkgs-postgresql
    #        if [ "`./result-pkgs-postgresql/bin/psql -lqt -p $(APP_DEV_POSTGRES_PORT) | cut -d \| -f 1 | grep $(APP_DEV_DBNAME)| wc -l`" != "1" ]; then \
    #                ./result-pkgs-postgresql/bin/createdb -p $(APP_DEV_POSTGRES_PORT) $(APP_DEV_DBNAME); \
    #        fi
    #        $(eval export DATABASE_URL=postgresql://localhost:$(APP_DEV_POSTGRES_PORT)/services)
    #        @echo "Using postgresql dev database $(DATABASE_URL)"


if __name__ == "__main__":
    cmd()
