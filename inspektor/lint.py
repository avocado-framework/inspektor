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

from pylint.lint import Run, PyLinter

from .path import PathChecker
from .utils import process

_PYLINT_HELP_TEXT = process.run('pylint --help', verbose=False).stdout


class QuietPyLinter(PyLinter):
    def read_config_file(self, *args, **kwargs):
        if getattr(self, 'quiet', None) is not None:
            # pylint: disable=E0203
            quiet = self.quiet
            try:
                self.quiet = 1
                return super(QuietPyLinter, self).read_config_file()
            finally:
                self.quiet = quiet

        return super(QuietPyLinter, self).read_config_file()


class QuietLintRun(Run):
    LinterClass = QuietPyLinter

    def __init__(self, *args, **kwargs):
        try:
            super(QuietLintRun, self).__init__(*args, **kwargs)
        except TypeError:
            kwargs.pop('exit')
            super(QuietLintRun, self).__init__(*args, **kwargs)


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
        if hasattr(args, 'parallel'):
            self.parallel = args.parallel
        else:
            import multiprocessing
            self.parallel = multiprocessing.cpu_count()
        # Be able to analyze all imports inside the project
        sys.path.insert(0, os.getcwd())
        self.log.info('Pylint disabled: %s', self.ignored_errors)
        self.log.info('Pylint enabled : %s', self.enabled_errors)

    @staticmethod
    def _pylint_has_option(option):
        return option in _PYLINT_HELP_TEXT

    def get_opts(self):
        """
        If VERBOSE is set, show pylint reports. If not, only an issue summary.
        """
        pylint_args = ['--rcfile=/dev/null',
                       '--good-names=i,j,k,Run,_,vm',
                       ('--msg-template='
                        '"{msg_id}:{line:3d},{column}: {obj}: {msg}"')]

        if self.ignored_errors:
            pylint_args.append('--disable=%s' % self.ignored_errors)
        if self.enabled_errors:
            pylint_args.append('--enable=%s' % self.enabled_errors)
        if self._pylint_has_option('--reports='):
            pylint_args.append('--reports=no')
        if self._pylint_has_option('--score='):
            pylint_args.append('--score=no')
        if self._pylint_has_option('--jobs='):
            pylint_args.append('--jobs=%s' % self.parallel)

        return pylint_args

    def check(self, file_or_dirs):
        def should_be_checked(path):
            checker = PathChecker(path=path, args=self.args, label='Lint',
                                  logger=self.log)
            return checker.check_attributes('text', 'python', 'not_empty')
        paths = []
        not_file_or_dirs = []
        for file_or_dir in file_or_dirs:
            if os.path.isdir(file_or_dir):
                for root, _, files in os.walk(file_or_dir):
                    for filename in files:
                        path = os.path.join(root, filename)
                        if should_be_checked(path):
                            paths.append(path)
            elif os.path.isfile(file_or_dir):
                if should_be_checked(file_or_dir):
                    paths.append(file_or_dir)
            else:
                not_file_or_dirs.append(file_or_dir)
        linter_failed = True
        if paths:
            runner = QuietLintRun(self.get_opts() + paths, exit=False)
            if hasattr(runner.linter.stats, 'get'):
                items = runner.linter.stats.get('by_module').items()
            else:
                items = runner.linter.stats.by_module.items()
            for module, status in items:
                status.pop("statement")
                if any(status.values()):
                    self.log.debug('Lint: %s FAIL', module)
                else:
                    self.log.debug('Lint: %s PASS', module)
            if runner.linter.msg_status == 0:
                linter_failed = False
        if not_file_or_dirs:
            self.log.error("Following arguments are not files nor dirs: %s",
                           ", ".join(not_file_or_dirs))
            return 0
        if linter_failed:
            return 0
        return 1
