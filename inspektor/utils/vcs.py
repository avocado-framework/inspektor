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

"""
Module that has models for version control systems, for inspektor scripts.
"""
import logging
import os

from . import ask
from . import exceptions
from . import process


class VCS(object):

    """
    Abstraction layer to the version control system.
    """

    def __init__(self):
        """
        Guess the version control system and instantiate it.
        """
        self.log = logging.getLogger("inspektor.vcs")
        self.backend = self.get_backend()
        self.cwd = os.getcwd()

    def get_backend(self):
        if os.path.isdir(".svn"):
            return SubVersionBackend()
        elif os.path.exists(".git"):
            return GitBackend()
        else:
            self.log.error("Could not figure version control system. You "
                           "must be at the top of the project's directory")
            return 1

    def get_repo_name(self):
        """
        Get the repository name
        """
        return self.backend.get_repo_name()

    def get_unknown_files(self):
        """
        Return a list of files unknown to the VCS.
        """
        return self.backend.get_unknown_files()

    def get_modified_files(self):
        """
        Return a list of files that were modified, according to the VCS.
        """
        return self.backend.get_modified_files()

    def is_file_tracked(self, fl):
        """
        Return whether a file is tracked by the VCS.
        """
        return self.backend.is_file_tracked(fl)

    def add_untracked_file(self, fl):
        """
        Add an untracked file to version control.
        """
        return self.backend.add_untracked_file(fl)

    def revert_file(self, fl):
        """
        Restore file according to the latest state on the reference repo.
        """
        return self.backend.revert_file(fl)

    def set_file_executable(self, fl):
        """
        Set executable permissions for file inside version control.
        """
        return self.backend.set_file_executable(fl)

    def unset_file_executable(self, fl):
        """
        Set executable permissions for file inside version control.
        """
        return self.backend.unset_file_executable(fl)

    def apply_patch(self, patch):
        """
        Applies a patch using the most appropriate method to the particular VCS.
        """
        return self.backend.apply_patch(patch)

    def update(self):
        """
        Updates the tree according to the latest state of the public tree
        """
        return self.backend.update()

    def get_modified_files_patch(self, untracked_files_before, patch):
        """
        Get modified files after a patch application.

        :param untracked_files_before: List of files untracked previous to
                patch application.
        """
        return self.backend.get_modified_files_patch(untracked_files_before,
                                                     patch)


class SubVersionBackend(object):

    """
    Implementation of a subversion backend for use with the VCS layer.
    """

    def __init__(self):
        self.log = logging.getLogger('inspektor.vcs')
        self.name = 'subversion'
        self.ignored_extension_list = ['.orig', '.bak']

    def get_repo_name(self):
        """
        Get the repository name
        """
        raise NotImplementedError

    def get_unknown_files(self):
        result = process.run("svn status --ignore-externals", verbose=False)
        unknown_files = []
        for line in result.stdout.split("\n"):
            status_flag = line.split()[0]
            if line and status_flag == "?":
                for extension in self.ignored_extension_list:
                    if not line.endswith(extension):
                        unknown_files.append(line[1:].strip())
        return unknown_files

    def get_modified_files(self):
        result = process.run("svn status --ignore-externals", verbose=False)
        modified_files = []
        for line in result.stdout.split("\n"):
            status_flag = line.split()[0]
            if line and status_flag == "M" or status_flag == "A":
                modified_files.append(line[1:].strip())
        return modified_files

    def is_file_tracked(self, fl):
        stdout = None
        try:
            result = process.run("svn status --ignore-externals %s" % fl,
                                 verbose=False)
            stdout = result.stdout
        except exceptions.CmdError:
            return False

        if stdout is not None:
            if stdout:
                status_flag = stdout.split()[0]
                if status_flag == "?":
                    return False
                else:
                    return True
            else:
                return True
        else:
            return False

    def add_untracked_file(self, fl):
        """
        Add an untracked file under revision control.

        :param file: Path to untracked file.
        """
        try:
            process.run('svn add %s' % fl, verbose=False)
        except exceptions.CmdError as e:
            self.log.error("Problem adding file %s to svn: %s", fl, e)
            return 1

    def revert_file(self, fl):
        """
        Revert file against last revision.

        :param file: Path to file to be reverted.
        """
        try:
            process.run('svn revert %s' % fl, verbose=False)
        except exceptions.CmdError as e:
            self.log.error("Problem reverting file %s: %s", fl, e)
            return 1

    def set_file_executable(self, fl):
        """
        Set executable permissions for file inside version control.
        """
        process.run("svn propset svn:executable ON %s" % fl,
                    ignore_status=True)

    def unset_file_executable(self, fl):
        """
        Unset executable permissions for file inside version control.
        """
        process.run("svn propdel svn:executable %s" % fl,
                    ignore_status=True)

    def apply_patch(self, patch):
        """
        Apply a patch to the code base. Patches are expected to be made using
        level -p1, and taken according to the code base top level.

        :param patch: Path to the patch file.
        """
        try:
            process.run("patch -p1 < %s" % patch, verbose=False)
        except Exception:
            self.log.error("Patch applied incorrectly. Possible causes: ")
            self.log.error("1 - Patch might not be -p1")
            self.log.error("2 - You are not at the top of the tree")
            self.log.error("3 - Patch was made using an older tree")
            self.log.error("4 - Mailer might have messed the patch")
            return 1

    def update(self):
        try:
            process.run("svn update")
        except exceptions.CmdError as details:
            self.log.error("SVN tree update failed: %s", details)

    def get_modified_files_patch(self, untracked_files_before, patch):
        """
        Get modified files after a patch application.

        :param untracked_files_before: List of files untracked previous to
                patch application.
        :param patch: Path to the patch file. Unused in the svn implementation.
        """
        untracked_files = self.get_unknown_files()
        modified_files = self.get_modified_files()
        add_to_vcs = []
        for untracked_file in untracked_files:
            if untracked_file not in untracked_files_before:
                add_to_vcs.append(untracked_file)

        if add_to_vcs:
            self.log.info("The files: ")
            for untracked_file in add_to_vcs:
                self.log.info(untracked_file)
            self.log.info("Might need to be added to svn")
            answer = ask("Would you like to add them to svn ?")
            if answer == "y":
                for untracked_file in add_to_vcs:
                    self.add_untracked_file(untracked_file)
                    modified_files.append(untracked_file)
            elif answer == "n":
                pass

        return modified_files


class GitBackend(object):

    """
    Implementation of a git backend for use with the VCS abstraction layer.
    """

    def __init__(self):
        self.ignored_extension_list = ['.orig', '.bak']
        self.name = 'git'
        self.log = logging.getLogger("inspektor.vcs")

    def get_repo_name(self):
        """
        Get the repository name from git remote command output.
        """
        cmd = "git remote -v | head -n1 | awk '{print $2}'"
        cmd += " | sed -e 's,.*:\\(.*/\\)\\?,,' -e 's/\\.git$//'"
        return process.run(cmd, verbose=False, shell=True).stdout.strip()

    def get_unknown_files(self):
        result = process.run("git status --porcelain", verbose=False)
        unknown_files = []
        for line in result.stdout.split("\n"):
            if line:
                status_flag = line.split()[0]
                if status_flag == "??":
                    for extension in self.ignored_extension_list:
                        if not line.endswith(extension):
                            element = line[2:].strip()
                            if element not in unknown_files:
                                unknown_files.append(element)
        return unknown_files

    def get_modified_files(self):
        result = process.run("git status --porcelain", verbose=False)
        modified_files = []
        for line in result.stdout.split("\n"):
            if line:
                status_flag = line.split()[0]
                if status_flag in ["M", "A"]:
                    modified_files.append(line.split()[-1])
        return modified_files

    def is_file_tracked(self, fl):
        try:
            process.run("git ls-files %s --error-unmatch" % fl, verbose=False)
            return True
        except exceptions.CmdError:
            return False

    def add_untracked_file(self, fl):
        """
        Add an untracked file under revision control.

        :param file: Path to untracked file.
        """
        try:
            process.run('git add %s' % fl, verbose=False)
        except exceptions.CmdError as e:
            self.log.error("Problem adding file %s to git: %s", fl, e)
            return 1

    def revert_file(self, fl):
        """
        Revert file against last revision.

        :param file: Path to file to be reverted.
        """
        try:
            process.run('git checkout %s' % fl, verbose=False)
        except exceptions.CmdError as e:
            self.log.error("Problem reverting file %s: %s", fl, e)
            return 1

    def set_file_executable(self, fl):
        """
        Set executable permissions for file inside version control.
        """
        process.run("chmod +x %s" % fl, ignore_status=True)

    def unset_file_executable(self, fl):
        """
        Unset executable permissions for file inside version control.
        """
        process.run("chmod -x %s" % fl, ignore_status=True)

    def apply_patch(self, patch):
        """
        Apply a patch to the code base using git am.

        A new branch will be created with the patch name.

        :param patch: Path to the patch file.
        """
        def branch_suffix(name):
            suffix = 1
            while not process.run("git show-ref --verify --quiet "
                                  "refs/heads/%s_%s" % (branch, suffix),
                                  verbose=False,
                                  ignore_status=True).exit_status:
                suffix += 1
            return "%s_%s" % (name, suffix)
        process.run("git checkout master", verbose=False)
        branch = os.path.basename(patch).rstrip(".patch")
        try:
            process.run("git checkout -b %s" % branch,
                        verbose=False)
        except exceptions.CmdError:
            self.log.error("branch %s already exists!", branch)
            answer = ask("What would you like to do?",
                         options="Abort/Delete/Rename/OldBase/NewBase")
            if not answer:
                answer = "A"
            answer = answer[0].upper()
            if answer == "A":
                self.log.info("Aborting check")
                return 1
            elif answer == "D":
                self.log.info("Deleting branch %s", branch)
                process.run("git branch -D %s" % branch, verbose=False)
                process.run("git checkout -b %s" % branch, verbose=False)
            elif answer == "R":     # Rename the old branch
                old_branch = branch_suffix(branch)
                self.log.info("Moving branch %s to %s", branch, old_branch)
                process.run("git branch -M %s %s"
                            % (branch, old_branch), verbose=False)
                process.run("git checkout -b %s" % branch, verbose=False)
            elif answer == "O":     # Rename the old branch and use old master
                old_branch = branch_suffix(branch)
                self.log.info("Moving branch %s to %s", branch, old_branch)
                process.run("git branch -M %s %s"
                            % (branch, old_branch), verbose=False)
                process.run("git checkout -b %s" % branch, verbose=False)
                base = process.run("git merge-base %s %s"
                                   % (branch, old_branch),
                                   verbose=False).stdout.strip()
                self.log.info("Last common base is %s", base)
                process.run("git reset --hard %s" % base, verbose=False)
            elif answer == "N":     # Rename and rebase the old branch
                old_branch = branch_suffix(branch)
                self.log.info("Moving branch %s to %s and rebasing it to "
                              "the current master", branch, old_branch)
                process.run("git branch -M %s %s"
                            % (branch, old_branch), verbose=False)
                process.run("git checkout %s" % old_branch, verbose=False)
                ret = process.run("git rebase master", verbose=False,
                                  ignore_status=True)
                if ret.exit_status:
                    self.log.error("Fail to automatically rebase old branch "
                                   "%s to the current master. Continuing "
                                   "without automatic rebase (as if you'd "
                                   "chosen 'Rename')", old_branch)
                    process.run("git rebase --abort", verbose=False,
                                ignore_status=True)
                process.run("git checkout master", verbose=False)
                process.run("git checkout -b %s" % branch, verbose=False)
        try:
            process.run("git am -3 %s" % patch, verbose=False)
        except exceptions.CmdError as details:
            self.log.error("Failed to apply patch to the git repo: %s",
                           details)
            return 1

    def update(self):
        try:
            process.run("git pull", verbose=False)
        except exceptions.CmdError as details:
            self.log.error("git tree update failed: %s", details)

    def get_modified_files_patch(self, untracked_files_before, patch):
        """
        Get modified files after a patch application.

        :param untracked_files_before: List of files untracked before patch
                application. Unused in the git implementation because git is
                awesome and we really don't need to keep track of them. This
                is here just for symmetry with subversion.
        :param patch: Path to the patch file.
        """
        modified_files = []
        patch_contents = open(patch, 'r')
        for line in patch_contents.readlines():
            if line.startswith("diff --git"):
                m_file = line.split()[-1][2:]
                if m_file not in modified_files:
                    modified_files.append(m_file)
        patch_contents.close()
        return modified_files
