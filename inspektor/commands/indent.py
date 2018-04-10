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
import os

from cliff.command import Command

from inspektor.indent import Reindenter


class IndentCommand(Command):
    """
    check for correct file indentation
    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(IndentCommand, self).get_parser(prog_name)
        parser.add_argument('path', type=str,
                            help='Path to check (empty for full tree check)',
                            nargs='*',
                            default=None)
        parser.add_argument('--fix', action='store_true', default=False,
                            help='Fix any indentation problems found')
        parser.add_argument('--exclude', type=str,
                            help='Quoted string containing paths or '
                                 'patterns to be excluded from '
                                 'checking, comma separated')
        return parser

    def take_action(self, parsed_args):
        if not parsed_args.path:
            parsed_args.path = [os.getcwd()]

        reindenter = Reindenter(parsed_args, logger=self.log)

        status = True
        for path in parsed_args.path:
            status &= reindenter.check(path)
        if status:
            self.log.info('Indentation check PASS')
            return 0
        else:
            self.log.error('Syntax check FAIL')
            return 1
