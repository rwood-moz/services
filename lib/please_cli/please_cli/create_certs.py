# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import click
import os

import please_cli.config


@click.command()
def cmd(app):
    pass
    # TODO
    #build-certs: tmpdir build-tool-createcert
    #	@if [ ! -e "$$PWD/tmp/ca.crt" ] && \
    #	   [ ! -e "$$PWD/tmp/ca.key" ] && \
    #	   [ ! -e "$$PWD/tmp/ca.srl" ] && \
    #	   [ ! -e "$$PWD/tmp/server.crt" ] && \
    #	   [ ! -e "$$PWD/tmp/server.key" ]; then \
    #	  ./result-tool-createcert/bin/createcert $$PWD/tmp; \
    #	fi


if __name__ == "__main__":
    cmd()
