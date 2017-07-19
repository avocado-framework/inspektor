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


class StyleChecker(object):

    def __init__(self, args, logger=logging.getLogger('')):
        self.args = args
        # Be able to analyze all imports inside the project
        sys.path.insert(0, os.getcwd())
        self.log = logger
        self.failed_paths = []
        self.log.info('PEP8 disabled: %s' % self.args.disable)

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
            self.log.error('Unexpected exception while checking %s', path)
            exc_info = sys.exc_info()
            stacktrace.log_exc_info(exc_info, 'inspektor.style')
            status = 1

        if status != 0:
            self.log.error('Style check fail: %s', path)
            self.failed_paths.append(path)
            if AUTOPEP8_CAPABLE:
                if self.args.fix:
                    self.log.info('Trying to fix errors with autopep8')
                    try:
                        process.run('autopep8 --in-place --max-line-length=%s --ignore %s %s' % (self.args.max_line_length, self.args.disable, path))
                    except Exception:
                        self.log.error('Unable to fix errors')
                        exc_info = sys.exc_info()
                        stacktrace.log_exc_info(exc_info, 'inspektor.style')
            else:
                self.log.error('Python library autopep8 not installed. '
                               'Please install it if you want to use --fix')

        return status == 0

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)
        else:
            self.log.error("Invalid location '%s'", path)
            return False


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
        parser.add_argument('--verbose', action='store_true',
                            help='Print extra debug messages')
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
