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

from cliff.command import Command

from inspektor.check import GithubPatchChecker


class GithubCommand(Command):
    """
    check github pull requests
    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(GithubCommand, self).get_parser(prog_name)
        parser.add_argument('gh_id', type=int,
                            help='GitHub Pull Request ID')
        parser.add_argument('-p', '--parent-project', type=str,
                            help=('Github organization. '
                                  'Default: %(default)s'),
                            default='avocado-framework')
        parser.add_argument('--disable', type=str,
                            help='Disable the pylint errors. Default: %(default)s',
                            default='W,R,C,E1002,E1101,E1103,E1120,F0401,I0011')
        parser.add_argument('--enable', type=str,
                            help=('Enable the pylint errors '
                                  '(takes place after disabled items are '
                                  'processed). Default: %(default)s'),
                            default='W0611')
        parser.add_argument('--pep8-disable', type=str,
                            help='Disable the pep8 errors. Default: %(default)s',
                            default='E501,E265,W601,E402')
        parser.add_argument('--exclude', type=str,
                            help='Quoted string containing paths or '
                                 'patterns to be excluded from '
                                 'checking, comma separated')
        parser.add_argument('--verbose', action='store_true',
                            help='Print extra debug messages')
        return parser

    def take_action(self, parsed_args):
        checker = GithubPatchChecker(parsed_args, logger=self.log)
        checker.validate()
        return checker.check()
