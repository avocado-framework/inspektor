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

import pep8

try:
    import autopep8
    AUTOPEP8_CAPABLE = True
except ImportError:
    AUTOPEP8_CAPABLE = False

from inspector import PathInspector

log = logging.getLogger("inspektor.style")


class StyleChecker(object):

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.ignored_errors = 'E501,E265,W601,E402'
        # Be able to analyze all imports inside the project
        sys.path.insert(0, os.getcwd())
        self.failed_paths = []

    def set_verbose(self):
        self.verbose = True

    def check_dir(self, path):
        """
        Recursively go on a directory checking files with PEP8.

        :param path: Path to a directory.
        """
        def visit(arg, dirname, filenames):
            for filename in filenames:
                self.check_file(os.path.join(dirname, filename))

        os.path.walk(path, visit, None)
        return not self.failed_paths

    def check_file(self, path):
        """
        Check one regular file with pylint for py syntax errors.

        :param path: Path to a regular file.
        :return: False, if pylint found syntax problems, True, if pylint didn't
                 find problems, or path is not a python module or script.
        """
        inspector = PathInspector(path)
        if inspector.is_toignore():
            return True
        if not inspector.is_python():
            return True
        try:
            opt_obj = pep8.StyleGuide().options
            ignore_list = self.ignored_errors.split(',') + list(opt_obj.ignore)
            opt_obj.ignore = tuple(set(ignore_list))
            # pylint: disable=E1123
            runner = pep8.Checker(filename=path, options=opt_obj)
        except:
            opts = ['--ignore'] + self.ignored_errors.split(',')
            pep8.process_options(opts)
            runner = pep8.Checker(filename=path)
        status = runner.check_all()
        if status != 0:
            log.error('PEP8 check fail: %s', path)
            self.failed_paths.append(path)
            if AUTOPEP8_CAPABLE:
                log.error('Trying to fix errors with autopep8')
                try:
                    opt_obj = autopep8.parse_args([path,
                                                   '--ignore',
                                                   self.ignored_errors,
                                                   '--in-place'])
                    autopep8.fix_file(path, opt_obj)
                except Exception, details:
                    log.error('Not able to fix errors: %s', details)
        return status == 0

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)


def set_arguments(parser):
    pstyle = parser.add_parser('style',
                               help='check code compliance to PEP8')
    pstyle.add_argument('path', type=str,
                        help='Path to check (empty for full tree check)',
                        nargs='*',
                        default=None)
    pstyle.set_defaults(func=run_style)


def run_style(args):
    paths = args.path
    if not paths:
        paths = [os.getcwd()]

    style_checker = StyleChecker(verbose=args.verbose)

    status = True
    for path in paths:
        status &= style_checker.check(path)
    if status:
        log.info("PEP8 compliance check PASS")
        return 0
    else:
        log.error("PEP8 compliance FAIL")
        return 1
