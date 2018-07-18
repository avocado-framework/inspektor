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
from inspektor.license import LicenseChecker
from inspektor.license import default_license
from inspektor.license import license_mapping
from inspektor.lint import Linter
from inspektor.style import StyleChecker


class CheckAllCommand(Command):
    """
    check indentation, style, lint and (optionally) license headers
    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckAllCommand, self).get_parser(prog_name)
        parser.add_argument('path', type=str,
                            help='Path to check (empty for full tree check)',
                            nargs='*',
                            default=None)
        parser.add_argument('--disable-style', type=str,
                            help='Disable the style errors given as arguments. '
                                 'Default: %(default)s',
                            default='E501,E265,W601,E402')
        parser.add_argument('--disable-lint', type=str,
                            help='Disable the pylint errors. Default: %(default)s',
                            default='W,R,C,E1002,E1101,E1103,E1120,F0401,I0011')
        parser.add_argument('--enable-lint', type=str,
                            help=('Enable the pylint errors '
                                  '(takes place after disabled items are '
                                  'processed). Default: %(default)s'),
                            default='W0611')
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
        parser.add_argument('--no-license-check', action='store_true', default=False,
                            help='Do not perform license check')
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
        return parser

    def take_action(self, parsed_args):
        checked_paths = parsed_args.path
        if not checked_paths:
            checked_paths = [os.getcwd()]

        reindenter = Reindenter(parsed_args, logger=self.log)
        style_checker = StyleChecker(parsed_args, logger=self.log)
        linter = Linter(parsed_args, logger=self.log)
        if not parsed_args.no_license_check:
            self.log.info('License check: (%s)', parsed_args.license)
            license_checker = LicenseChecker(parsed_args, logger=self.log)
        else:
            self.log.info('License check: disabled')
            license_checker = None

        status = True
        for path in checked_paths:
            status &= reindenter.check(path=path)
            status &= style_checker.check(path=path)
            if license_checker is not None:
                status &= license_checker.check(path=path)
        status &= linter.check(checked_paths)

        if status:
            self.log.info('Global check PASS')
            return 0
        else:
            self.log.error('Global check FAIL')
            return 1
