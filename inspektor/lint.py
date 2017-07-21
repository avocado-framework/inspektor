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

from pylint.lint import Run

from .path import PathChecker


class Linter(object):

    def __init__(self, args, logger=logging.getLogger('')):
        self.ignored_errors = ''
        if hasattr(args, 'disable'):
            self.ignored_errors = args.disable
        elif hasattr(args, 'disable_lint'):
            self.ignored_errors = args.disable_lint
        self.enabled_errors = ''
        if hasattr(args, 'enable'):
            self.enabled_errors = args.enable
        elif hasattr(args, 'enable_lint'):
            self.enabled_errors = args.enable_lint
        self.log = logger
        self.args = args
        self.verbose = args.verbose
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
            if self.ignored_errors:
                pylint_args.append('--disable=%s' % self.ignored_errors)
            if self.enabled_errors:
                pylint_args.append('--enable=%s' % self.enabled_errors)
            pylint_args.append('--reports=no')
            if sys.version_info[:2] > (2, 6):
                pylint_args.append('--score=no')

        return pylint_args

    def check_dir(self, path):
        """
        Recursively go on a directory checking files with pylint.

        :param path: Path to a directory.
        """
        for root, dirs, files in os.walk(path):
            for filename in files:
                self.check_file(os.path.join(root, filename))

        return not self.failed_paths

    def check_file(self, path):
        """
        Check one regular file with pylint for py syntax errors.

        :param path: Path to a regular file.
        :return: False, if pylint found syntax problems, True, if pylint didn't
                 find problems, or path is not a python module or script.
        """
        checker = PathChecker(path=path, args=self.args, label='Lint')
        if not checker.check_attributes('text', 'python', 'not_empty'):
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
