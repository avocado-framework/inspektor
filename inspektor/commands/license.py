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

from inspektor.license import LicenseChecker
from inspektor.license import default_license
from inspektor.license import license_mapping


class LicenseCommand(Command):
    """
    check for license headers
    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(LicenseCommand, self).get_parser(prog_name)
        parser.add_argument('path', type=str,
                            help='Path to check (empty for full tree check)',
                            nargs='?',
                            default="")
        parser.add_argument('--license', type=str,
                            help=('License type. Supported license types: %s. '
                                  'Default: %s' %
                                  (license_mapping.keys(), default_license)),
                            default="gplv2_later")
        parser.add_argument('--copyright', type=str,
                            help='Copyright string. Ex: "Copyright (c) 2013-2014 FooCorp"',
                            default="")
        parser.add_argument('--author', type=str,
                            help='Author string. Ex: "Author: Brandon Lindon <brandon.lindon@foocorp.com>"',
                            default="")
        parser.add_argument('--exclude', type=str,
                            help='Quoted string containing paths or '
                                 'patterns to be excluded from '
                                 'checking, comma separated')
        parser.add_argument('--fix', action='store_true', default=False,
                            help='Fix any style problems found '
                                 '(needs autopep8 installed)')
        return parser

    def take_action(self, parsed_args):
        path = parsed_args.path

        if not path:
            path = os.getcwd()

        checker = LicenseChecker(parsed_args)

        if checker.check(path):
            self.log.info("License check PASS")
            return 0
        else:
            self.log.error("License check FAIL")
            return 1
