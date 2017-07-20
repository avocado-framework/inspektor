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

import fnmatch
import os
import stat

PY_EXTENSIONS = ['.py']
SHEBANG = '#!'


class PathChecker(object):

    def __init__(self, path, args):
        self.args = args
        self.path = path
        self.ignore = ['*~', '*#', '*.swp', '*.py?', '*.o', '.git', '.svn']
        if self.args.exclude:
            self.ignore += self.args.exclude.split(',')
        self._read_gitignore()

    def _read_gitignore(self):
        config_ignore = '{home}/.config/git/ignore'.format(
            home=os.environ.get('HOME'))
        git_dir_ignore = '{gitdir}/.config/git/ignore'.format(
            gitdir=os.environ.get('GIT_DIR'))
        dot_ignore = '.gitignore'
        for ign in (dot_ignore, git_dir_ignore, config_ignore):
            if os.path.isfile(ign):
                with open(ign) as f:
                    self.ignore += [x.strip() for x in f.readlines()]
                break
        self.ignore = list(set(self.ignore))

    def get_first_line(self):
        first_line = ""
        if os.path.isfile(self.path):
            checked_file = open(self.path, "r")
            first_line = checked_file.readline()
            checked_file.close()
        return first_line

    def has_exec_permission(self):
        mode = os.stat(self.path)[stat.ST_MODE]
        return mode & stat.S_IXUSR

    def is_empty(self):
        size = os.stat(self.path)[stat.ST_SIZE]
        return size == 0

    def is_script(self, language=None):
        first_line = self.get_first_line()
        if first_line:
            if first_line.startswith(SHEBANG):
                if language is None:
                    return True
                elif language in first_line:
                    return True
        return False

    def is_python(self):
        for extension in PY_EXTENSIONS:
            if self.path.endswith(extension):
                return True

        return self.is_script(language='python')

    def is_toignore(self):
        path = self.path
        if path.startswith('./'):
            path = path[2:]
        for pattern in self.ignore:
            if fnmatch.fnmatch(path, pattern):
                return True
            if self.path.startswith(os.path.abspath(pattern)):
                return True
        return False
