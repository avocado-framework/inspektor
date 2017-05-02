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

import pycodestyle

try:
    import autopep8
    AUTOPEP8_CAPABLE = True
    del(autopep8)
except ImportError:
    AUTOPEP8_CAPABLE = False

from .inspector import PathInspector
from . import stacktrace
from .utils import process

log = logging.getLogger("inspektor.style")


class StyleChecker(object):

    def __init__(self, args):
        self.args = args
        # Be able to analyze all imports inside the project
        sys.path.insert(0, os.getcwd())
        self.failed_paths = []
        log.info('PEP8 disabled: %s' % self.args.disable)

    def check_dir(self, path):
        """
        Recursively go on a directory checking files with PEP8.

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
            opt_obj = pycodestyle.StyleGuide().options
            ignore_list = self.args.disable.split(',') + list(opt_obj.ignore)
            opt_obj.ignore = tuple(set(ignore_list))
            # pylint: disable=E1123
            runner = pycodestyle.Checker(filename=path, options=opt_obj)
            status = runner.check_all()
        except Exception:
            log.error('Unexpected exception while checking %s', path)
            exc_info = sys.exc_info()
            stacktrace.log_exc_info(exc_info, 'inspektor.style')
            status = 1

        if status != 0:
            log.error('Style check fail: %s', path)
            self.failed_paths.append(path)
            if AUTOPEP8_CAPABLE:
                if self.args.fix:
                    log.info('Trying to fix errors with autopep8')
                    try:
                        process.run('autopep8 --in-place --max-line-length=%s --ignore %s %s' % (self.args.max_line_length, self.args.disable, path))
                    except Exception:
                        log.error('Unable to fix errors')
                        exc_info = sys.exc_info()
                        stacktrace.log_exc_info(exc_info, 'inspektor.style')

        return status == 0

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)
        else:
            log.error("Invalid location '%s'", path)
            return False


def run_style(args):
    paths = args.path
    if not paths:
        paths = [os.getcwd()]

    style_checker = StyleChecker(args)

    status = True
    for path in paths:
        status &= style_checker.check(path)
    if status:
        log.info("PEP8 compliance check PASS")
        return 0
    else:
        log.error("PEP8 compliance FAIL")
        return 1


def set_arguments(parser):
    command = 'style'
    pstyle = parser.add_parser(command,
                               help='check code compliance to PEP8')
    pstyle.add_argument('path', type=str,
                        help='Path to check (empty for full tree check)',
                        nargs='*',
                        default=None)
    pstyle.add_argument('--disable', type=str,
                        help='Disable the pep8 errors. Default: %(default)s',
                        default='E501,E265,W601,E402')
    pstyle.add_argument('--fix', action='store_true', default=False,
                        help='Fix any style problems found (with autopep8)')
    pstyle.add_argument('--max-line-length', type=int, default=79,
                        help=('set maximum allowed line length. Default: '
                              '%(default)s'))
    return (command, run_style)
