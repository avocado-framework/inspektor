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

import logging
import multiprocessing
import os

from cliff.command import Command

from inspektor.lint import Linter


class LintCommand(Command):
    """
    check for errors with pylint
    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(LintCommand, self).get_parser(prog_name)
        parser.add_argument('path', type=str,
                            help='Path to check (empty for full tree check)',
                            nargs='*',
                            default=None)
        parser.add_argument('--disable', type=str,
                            help='Disable the pylint errors. Default: %(default)s',
                            default='W,R,C,E1002,E1101,E1103,E1120,F0401,I0011')
        parser.add_argument('--enable', type=str,
                            help=('Enable the pylint errors '
                                  '(takes place after disabled items are '
                                  'processed). Default: %(default)s'),
                            default='W0611')
        parser.add_argument('--exclude', type=str,
                            help='Quoted string containing paths or '
                                 'patterns to be excluded from '
                                 'checking, comma separated')
        parser.add_argument('--parallel', action='store', nargs='?',
                            default=multiprocessing.cpu_count(),
                            help="How many threads to use")
        return parser

    def take_action(self, parsed_args):
        if not parsed_args.path:
            parsed_args.path = [os.getcwd()]

        linter = Linter(parsed_args, logger=self.log)
        status = linter.check(parsed_args.path)

        if status:
            self.log.info("Syntax check PASS")
            return 0
        else:
            self.log.error("Syntax check FAIL")
            return 1
