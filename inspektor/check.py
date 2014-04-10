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

from inspektor import lint
from inspektor import reindent
from inspektor import style
from inspektor import inspector
from inspektor import vcs
from inspektor import utils

TMP_FILE_DIR = tempfile.gettempdir()
LOG_FILE_PATH = os.path.join(TMP_FILE_DIR, 'check-patch.log')
# Hostname of patchwork server to use
PWHOST = "patchwork.virt.bos.redhat.com"

log = logging.getLogger("inspektor.check")

# Rely on built-in recursion limit to limit number of directories searched


def license_project_name(path):
    '''
    Locate the nearest LICENSE file, take first word as the project name
    '''
    if path == '/' or path == '.':
        raise RuntimeError('Ran out of directories searching for LICENSE file')
    try:
        license_file = file(os.path.join(path, 'LICENSE'), 'r')
        first_word = license_file.readline().strip().split()[0].lower()
        return first_word, path
    except IOError:
        # Recurse search parent of path's directory
        return license_project_name(os.path.dirname(path))


class FileChecker(object):

    """
    Picks up a given file and performs various checks, looking after problems
    and eventually applying solutions when all possible.
    """

    def __init__(self):
        """
        Class constructor, sets the file checkers.

        :param path: Path to the file that will be checked.
        :param vcs: Version control system being used.
        :param confirm: Whether to answer yes to all questions asked without
                prompting the user.
        """
        self.linter = lint.Linter(verbose=False)
        self.indenter = reindent.Reindenter(verbose=False)
        self.style_checker = style.StyleChecker()
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
        path_inspector = inspector.PathInspector(path)
        path_is_script = path_inspector.is_script()
        path_is_exec = path_inspector.has_exec_permission()
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

    def __init__(self, patch=None, patchwork_id=None, github_id=None):
        FileChecker.__init__(self)
        self.base_dir = TMP_FILE_DIR

        if patch:
            self.patch = os.path.abspath(patch)

        if patchwork_id:
            self.patch = self._fetch_from_patchwork(patchwork_id)

        if github_id:
            self.patch = self._fetch_from_github(github_id)

    def validate(self):
        if not os.path.isfile(self.patch):
            logging.error("Invalid patch file %s provided. Aborting.",
                          self.patch)
            return 1

        changed_files_before = self.vcs.get_modified_files()
        if changed_files_before:
            log.error("Repository has changed files prior to patch "
                      "application")
            answer = utils.ask("Would you like to revert them?")
            if answer == "n":
                log.error("Not safe to proceed without reverting files.")
                return 1
            else:
                for changed_file in changed_files_before:
                    self.vcs.revert_file(changed_file)

        self.untracked_files = self.vcs.get_unknown_files()

    def _get_patchwork_url(self, pw_id):
        return "http://%s/patch/%s/mbox/" % (self.pwhost, pw_id)

    def _download_from_patchwork(self, pw_id):
        patch_url = self._get_patchwork_url(pw_id)
        patch_dest = os.path.join(self.base_dir, 'patchwork-%s.patch' %
                                  pw_id)
        return utils.download.get_file(patch_url, patch_dest)

    def _fetch_from_patchwork(self, pw_id):
        """
        Gets a patch file from patchwork and puts it under the cwd so it can
        be applied.

        :param pw_id: Patchwork patch id. It can be a string with
                comma separated patchwork ids.
        """
        collection = os.path.join(self.base_dir, 'patchwork-%s.patch' %
                                  utils.random_string(4))
        collection_rw = open(collection, 'w')

        for p_id in pw_id.split(","):
            patch = self._download_from_patchwork(p_id)
            # Patchwork sometimes puts garbage on the path, such as long
            # sequences of underscores (_______). Get rid of those.
            patch_ro = open(patch, 'r')
            patch_contents = patch_ro.readlines()
            patch_ro.close()
            for line in patch_contents:
                if not line.startswith("___"):
                    collection_rw.write(line)
        collection_rw.close()

        return collection

    def _get_github_project_name(self):
        project_name, _ = license_project_name(self.vcs.cwd)
        return project_name

    def _get_github_url(self, gh_id):
        """
        Gets the correct github URL for the given project.
        """
        return ("https://github.com/autotest/%s/pull/%s.patch" %
                (self._get_github_project_name(), gh_id))

    def _fetch_from_github(self, gh_id):
        """
        Gets a patch file from patchwork and puts it under the base dir.

        :param gh_id: Patchwork patch id.
        """
        patch_url = self._get_github_url(gh_id)
        patch_dest = os.path.join(self.base_dir, 'github-%s.patch' % gh_id)
        return utils.download.get_file(patch_url, patch_dest)

    def _check_files_modified_patch(self):
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
        return self._check_files_modified_patch()


def set_arguments(parser):
    pgh = parser.add_parser('github',
                            help='check GitHub Pull Requests')
    pgh.add_argument('gh_id', type=int,
                     help='GitHub Pull Request ID')
    pgh.set_defaults(func=check_patch_github)


def check_patch_github(args):
    gh_id = args.gh_id
    checker = PatchChecker(github_id=gh_id)
    checker.validate()
    if checker.check():
        log.info("Github ID #%s check PASS", gh_id)
        return 0
    else:
        log.info("Github ID #%s check FAIL", gh_id)
        return 1
