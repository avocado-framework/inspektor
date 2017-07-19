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

import logging
import os
import sys

try:
    from os.path import walk
except ImportError:
    from os import walk

from cliff.command import Command
from pylint.lint import Run

from .inspector import PathInspector


class Linter(object):

    def __init__(self, args, logger=logging.getLogger('')):
        assert args.disable is not None
        assert args.enable is not None
        self.log = logger
        self.args = args
        self.verbose = args.verbose
        self.ignored_errors = args.disable
        self.enabled_errors = args.enable
        # Be able to analyze all imports inside the project
        sys.path.insert(0, os.getcwd())
        self.failed_paths = []
        if not self.verbose:
            self.log.info('Pylint disabled: %s' % self.ignored_errors)
            self.log.info('Pylint enabled : %s' % self.enabled_errors)
        else:
            self.log.info('Verbose mode, no disable/enable, full reports')

    def set_verbose(self):
        self.verbose = True

    def get_opts(self):
        """
        If VERBOSE is set, show pylint reports. If not, only an issue summary.
        """
        pylint_args = ['--rcfile=/dev/null',
                       '--good-names=i,j,k,Run,_,vm',
                       ('--msg-template='
                        '"{msg_id}:{line:3d},{column}: {obj}: {msg}"')]

        if not self.verbose:
            if self.args.disable:
                pylint_args.append('--disable=%s' % self.ignored_errors)
            if self.args.enable:
                pylint_args.append('--enable=%s' % self.enabled_errors)
            pylint_args.append('--reports=no')

        return pylint_args

    def check_dir(self, path):
        """
        Recursively go on a directory checking files with pylint.

        :param path: Path to a directory.
        """
        def visit(arg, dirname, filenames):
            for filename in filenames:
                self.check_file(os.path.join(dirname, filename))

        walk(path, visit, None)
        return not self.failed_paths

    def check_file(self, path):
        """
        Check one regular file with pylint for py syntax errors.

        :param path: Path to a regular file.
        :return: False, if pylint found syntax problems, True, if pylint didn't
                 find problems, or path is not a python module or script.
        """
        inspector = PathInspector(path=path, args=self.args)
        if inspector.is_toignore():
            return True
        if not inspector.is_python():
            return True

        try:
            runner = Run(self.get_opts() + [path], exit=False)
            if runner.linter.msg_status != 0:
                self.log.error('Pylint check fail: %s', path)
                self.failed_paths.append(path)
            return runner.linter.msg_status == 0
        except Exception as details:
            self.log.error('Pylint check fail: %s (pylint exception: %s)',
                           path, details)
            self.failed_paths.append(path)
            return False

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)
        else:
            self.log.error("Invalid location '%s'", path)
            return False


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
        parser.add_argument('--verbose', action='store_true',
                            help='Print extra debug messages')
        return parser

    def take_action(self, parsed_args):
        if not parsed_args.path:
            parsed_args.path = [os.getcwd()]

        linter = Linter(parsed_args, logger=self.log)

        status = True
        for path in parsed_args.path:
            status &= linter.check(path)
        if status:
            self.log.info("Syntax check PASS")
            return 0
        else:
            self.log.error("Syntax check FAIL")
            return 1
