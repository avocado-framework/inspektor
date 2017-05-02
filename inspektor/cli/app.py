# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: Red Hat 2013-2014
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>

"""
Implements the base inspektor application.
"""
import logging
from argparse import ArgumentParser

from .. import lint
from .. import reindent
from .. import style
from .. import check
from .. import license

log = logging.getLogger("inspektor.app")

ERROR_INTERRUPTED = 3


class InspektorApp(object):

    """
    Basic inspektor application.
    """

    def __init__(self):
        self.arg_parser = ArgumentParser(description='Inspektor code check')
        self.arg_parser.add_argument('-v', '--verbose', action='store_true',
                                     help=('print extra debug messages '
                                           '(alters behavior of the lint '
                                           'subcommand)'),
                                     dest='verbose')
        self.arg_parser.add_argument('--exclude', type=str,
                                     help='Quoted string containing paths or '
                                          'patterns to be excluded from '
                                          'checking, comma separated')
        subparsers = self.arg_parser.add_subparsers(title='subcommands',
                                                    description='valid subcommands',
                                                    help='subcommand help')
        lint.set_arguments(subparsers)
        reindent.set_arguments(subparsers)
        style.set_arguments(subparsers)
        check.set_arguments(subparsers)
        license.set_arguments(subparsers)
        self.args = self.arg_parser.parse_args()

    def run(self):
        try:
            return self.args.func(self.args)
        except KeyboardInterrupt:
            log.error('User pressed Ctrl+C, exiting...')
            return ERROR_INTERRUPTED
