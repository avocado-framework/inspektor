import logging
import os
import sys

import pep8
import autopep8

from inspector import PathInspector

log = logging.getLogger("inspektor.style")


class StyleChecker(object):

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.ignored_errors = 'E501,W601'
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
        if not inspector.is_python():
            return True
        opt_obj = pep8.StyleGuide().options
        ignore_list = self.ignored_errors.split(',') + list(opt_obj.ignore)
        opt_obj.ignore = tuple(set(ignore_list))
        runner = pep8.Checker(filename=path, options=opt_obj)
        if runner.check_all() != 0:
            log.error('PEP8 check fail: %s', path)
            self.failed_paths.append(path)
            log.error('Trying to fix errors with autopep8')
            opt_obj = autopep8.parse_args([path,
                                           '--ignore',
                                           self.ignored_errors,
                                           '--in-place'])[0]
            autopep8.fix_file(path, options=opt_obj)
        return runner.check_all() == 0

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)


def run_style(args):
    path = args.path
    if not path:
        path = os.getcwd()

    style_checker = StyleChecker(verbose=args.verbose)

    if style_checker.check(path):
        log.info("Syntax check PASS")
        sys.exit(0)
    else:
        log.error("Syntax check FAIL")
        sys.exit(1)
