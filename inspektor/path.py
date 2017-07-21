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
import logging

PY_EXTENSIONS = ['.py']
SHEBANG = '#!'


class PathAttributes(object):
    def __init__(self, path, ignore_patterns):
        self._path = path
        self._ignore_patterns = ignore_patterns

    def __str__(self):
        return self._path

    def first_line(self):
        if os.path.isfile(self._path):
            with open(self._path, "r") as checked_file:
                return checked_file.readline()

    def executable(self):
        mode = os.stat(self._path)[stat.ST_MODE]
        return mode & stat.S_IXUSR

    def not_empty(self):
        return not self.empty()

    def empty(self):
        size = os.stat(self._path)[stat.ST_SIZE]
        return size == 0

    def script(self, language=None):
        first_line = self.first_line()
        if first_line:
            if first_line.startswith(SHEBANG):
                if language is None:
                    return True
                elif language in first_line:
                    return True
        return False

    def python(self):
        for extension in PY_EXTENSIONS:
            if self._path.endswith(extension):
                return True

        return self.script(language='python')

    def ignore(self):
        path = self._path
        if path.startswith('./'):
            path = path[2:]
        for pattern in self._ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
            if self._path.startswith(os.path.abspath(pattern)):
                return True
        return False


class PathChecker(object):

    def __init__(self, path, args, label=None, logger=logging.getLogger('')):
        self.args = args
        self.ignore = ['*~', '*#', '*.swp', '*.py?', '*.o', '.git', '.svn']
        if self.args.exclude:
            self.ignore += self.args.exclude.split(',')
        self._read_gitignore()
        self.path = PathAttributes(path, ignore_patterns=self.ignore)
        if label is None:
            label = 'Check'
        self.label = label
        self.log = logger

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

    def check_attributes(self, *args):
        if self.path.ignore():
            return False
        checks_passed = True
        for arg in args:
            checks_passed &= getattr(self.path, arg)()
        if checks_passed:
            self.log.debug('%s: %s', self.label, self.path)
        return checks_passed
