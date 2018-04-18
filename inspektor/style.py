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

import pycodestyle

try:
    import autopep8
    AUTOPEP8_CAPABLE = True
    del(autopep8)
except ImportError:
    AUTOPEP8_CAPABLE = False

from .path import PathChecker
from .utils import stacktrace
from .utils import process


class StyleChecker(object):

    def __init__(self, args, logger=logging.getLogger('')):
        # Be able to analyze all imports inside the project
        sys.path.insert(0, os.getcwd())
        self.log = logger
        self.failed_paths = []
        self.ignored_errors = ''
        if hasattr(args, 'disable'):
            self.ignored_errors = args.disable
        elif hasattr(args, 'disable_style'):
            self.ignored_errors = args.disable_style
        self.args = args
        self.log.info('PEP8 disabled: %s', self.ignored_errors)

    def check_dir(self, path):
        """
        Recursively go on a directory checking files with PEP8.

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
        checker = PathChecker(path=path, args=self.args, label='Style',
                              logger=self.log)
        if not checker.check_attributes('text', 'python', 'not_empty'):
            return True

        try:
            opt_obj = pycodestyle.StyleGuide().options
            ignore_list = self.ignored_errors.split(',') + list(opt_obj.ignore)
            opt_obj.ignore = tuple(set(ignore_list))
            # pylint: disable=E1123
            runner = pycodestyle.Checker(filename=path, options=opt_obj)
            status = runner.check_all()
        except Exception:
            self.log.error('Unexpected exception while checking %s', path)
            exc_info = sys.exc_info()
            stacktrace.log_exc_info(exc_info, 'inspektor.style')
            status = 1

        if status != 0:
            self.failed_paths.append(path)
            fix_status = ''
            if AUTOPEP8_CAPABLE:
                if self.args.fix:
                    self.log.info('Trying to fix errors with autopep8')
                    try:
                        process.run('autopep8 --in-place --max-line-length=%s --ignore %s %s' % (self.args.max_line_length, self.ignored_errors, path))
                        fix_status = 'FIX OK'
                    except Exception:
                        self.log.error('Unable to fix errors')
                        exc_info = sys.exc_info()
                        stacktrace.log_exc_info(exc_info, 'inspektor.style')
                        fix_status = 'FIX NOT OK'
            else:
                self.log.error('Python library autopep8 not installed. '
                               'Please install it if you want to use --fix')
                fix_status = 'FIX NOT OK'
            checker.log_status(status='FAIL', extra=fix_status)
        else:
            checker.log_status(status='PASS')

        return status == 0

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)
        else:
            self.log.error("Invalid location '%s'", path)
            return False
