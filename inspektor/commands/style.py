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

from inspektor.style import StyleChecker


class StyleCommand(Command):
    """
    check against style guide with pycodestyle
    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StyleCommand, self).get_parser(prog_name)
        parser.add_argument('path', type=str,
                            help='Path to check (empty for full tree check)',
                            nargs='*',
                            default=None)
        parser.add_argument('--disable', type=str,
                            help='Disable the PEP8 errors given as arguments. '
                                 'Default: %(default)s',
                            default='E501,E265,W601,E402')
        parser.add_argument('--fix', action='store_true', default=False,
                            help='Fix any style problems found '
                                 '(needs autopep8 installed)')
        parser.add_argument('--max-line-length', type=int, default=79,
                            help=('set maximum allowed line length. Default: '
                                  '%(default)s'))
        parser.add_argument('--exclude', type=str,
                            help='Quoted string containing paths or '
                                 'patterns to be excluded from '
                                 'checking, comma separated')
        return parser

    def take_action(self, parsed_args):
        paths = parsed_args.path
        if not paths:
            paths = [os.getcwd()]

        style_checker = StyleChecker(parsed_args, logger=self.log)

        status = True
        for path in paths:
            status &= style_checker.check(path)
        if status:
            self.log.info("PEP8 compliance check PASS")
            return 0
        else:
            self.log.error("PEP8 compliance FAIL")
            return 1
