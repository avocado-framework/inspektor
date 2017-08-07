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
import tempfile

from . import indent
from . import lint
from . import style
from . import utils
from .path import PathChecker
from .utils import vcs

TMP_FILE_DIR = tempfile.gettempdir()
LOG_FILE_PATH = os.path.join(TMP_FILE_DIR, 'check-patch.log')

# Rely on built-in recursion limit to limit number of directories searched


class FileChecker(object):

    """
    Picks up a given file and performs various checks, looking after problems
    and eventually applying solutions when all possible.
    """

    def __init__(self, args):
        """
        Class constructor, sets the file checkers.

        :param path: Path to the file that will be checked.
        :param vcs: Version control system being used.
        :param confirm: Whether to answer yes to all questions asked without
                prompting the user.
        """
        assert args.disable is not None
        assert args.pep8_disable is not None
        self.args = args
        self.linter = lint.Linter(self.args)
        self.indenter = indent.Reindenter(self.args)
        # Tweak --disable option for StyleChecker
        self.args.disable = self.args.pep8_disable
        self.style_checker = style.StyleChecker(self.args)
        self.vcs = vcs.VCS()

    def _check_indent(self, path):
        """
        Verifies the file with the reindent module.

        This tool performs the following checks on python files:

          * Trailing whitespaces
          * Tabs
          * End of line
          * Incorrect indentation

        And will automatically correct problems.
        """
        return self.indenter.check_file(path)

    def _check_syntax(self, path):
        """
        Verifies the file with pylint.
        """
        return self.linter.check_file(path)

    def _check_style(self, path):
        """
        Verifies the file compliance to PEP8.
        """
        return self.style_checker.check_file(path)

    def _check_permissions(self, path):
        """
        Verifies the execution permissions and fixes them if possible:

          * Files with no shebang and execution permissions will be fixed.
          * Files with shebang and no execution permissions will be fixed.
        """
        result = True
        if os.path.isdir(path):
            return result
        checker = PathChecker(path, self.args)
        path_is_script = checker.path.script
        path_is_exec = checker.path.executable
        if path_is_script:
            if not path_is_exec:
                result = False
                self.vcs.set_file_executable(path)
        else:
            if path_is_exec:
                result = False
                self.vcs.unset_file_executable(path)
        return result

    def check_file(self, path):
        """
        Executes all required checks, if problems are found, the possible
        corrective actions are listed.
        """
        return (self._check_syntax(path) and
                self._check_indent(path) and
                self._check_style(path) and
                self._check_permissions(path))


class PatchChecker(FileChecker):

    def __init__(self, args, patch=None,
                 logger=logging.getLogger('')):
        super(PatchChecker, self).__init__(args)
        self.base_dir = TMP_FILE_DIR
        self.log = logger
        self.patch = patch
        self.untracked_files = None

        if patch:
            self.patch = os.path.abspath(patch)

    def validate(self):
        if not os.path.isfile(self.patch):
            logging.error("Invalid patch file %s provided. Aborting.",
                          self.patch)
            return 1

        changed_files_before = self.vcs.get_modified_files()
        if changed_files_before:
            self.log.error("Repository has changed files prior to patch "
                           "application")
            answer = utils.ask("Would you like to revert them?")
            if answer == "n":
                self.log.error("Not safe to proceed without reverting files.")
                return 1
            else:
                for changed_file in changed_files_before:
                    self.vcs.revert_file(changed_file)

        self.untracked_files = self.vcs.get_unknown_files()

    def check_modified_files(self):
        files_failed_check = []

        modified_files = self.vcs.get_modified_files_patch(self.untracked_files,
                                                           self.patch)
        for modified_file in modified_files:
            # Additional safety check, new commits might introduce
            # new directories
            if os.path.isfile(modified_file):
                if not self.check_file(modified_file):
                    files_failed_check.append(modified_file)

        if files_failed_check:
            return False
        else:
            return True

    def check(self):
        self.vcs.apply_patch(self.patch)
        passed_check = self.check_modified_files()
        if passed_check:
            self.log.info('Patch %s check PASS', self.patch)
            return 0
        else:
            self.log.error('Patch %s check FAIL', self.patch)
            return 1
