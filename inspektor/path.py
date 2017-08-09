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
import codecs
from inspektor.utils.data_structures import Borg

PY_EXTENSIONS = ['.py']
SHEBANG = '#!'


class PathRegistry(Borg):

    def __init__(self):
        Borg.__init__(self)
        if not getattr(self, 'registry', None):
            self.registry = {}

    def get(self, path):
        return self.registry.get(path)

    def set(self, path_attribute):
        self.registry[path_attribute.path] = path_attribute


class PathAttribute(object):
    def __init__(self, path, ignore_patterns):
        path_registry = PathRegistry()
        cached_path_attribute = path_registry.get(path=path)
        if cached_path_attribute:
            self.__dict__ = cached_path_attribute.__dict__
        else:
            self._path = path
            self._ignore_patterns = ignore_patterns
            self._ignore = None
            self._text = None
            self._first_line = None
            self._executable = None
            self._empty = None
            self._python = None
            path_registry.set(self)

    def __str__(self):
        return self._path

    @property
    def path(self):
        return self._path

    @property
    def text(self):
        if self._text is not None:
            return self._text
        if self.ignore or self.first_line is None:
            self._text = False
            return self._text
        else:
            self._text = True
            return self._text

    @property
    def binary(self):
        return not self.text

    @property
    def first_line(self):
        if self._first_line is not None:
            return self._first_line

        if os.path.isfile(self._path):
            try:
                with codecs.open(self._path, 'r', encoding='utf-8') as checked_file:
                    self._first_line = checked_file.readline()
                    return self._first_line
            except UnicodeDecodeError:
                self._ignore = True
                self._text = False

    @property
    def executable(self):
        if self._executable is not None:
            return self._executable
        mode = os.stat(self._path)[stat.ST_MODE]
        self._executable = mode & stat.S_IXUSR
        return self._executable

    @property
    def not_empty(self):
        return not self.empty

    @property
    def empty(self):
        if self._empty is not None:
            return self._empty
        size = os.stat(self._path)[stat.ST_SIZE]
        self._empty = size == 0
        return self._empty

    def script(self, language=None):
        if self.first_line:
            if self.first_line.startswith(SHEBANG):
                if language is None:
                    return True
                elif language in self.first_line:
                    return True
        return False

    @property
    def python(self):
        if self._python is not None:
            return self._python
        for extension in PY_EXTENSIONS:
            if self._path.endswith(extension):
                self._python = True
                return self._python

        return self.script(language='python')

    @property
    def ignore(self):
        if self._ignore is not None:
            return self._ignore
        else:
            path = self._path
            if path.startswith('./'):
                path = path[2:]
            for pattern in self._ignore_patterns:
                if fnmatch.fnmatch(path, pattern):
                    self._ignore = True
                if self._path.startswith(os.path.abspath(pattern)):
                    self._ignore = True
            if self._ignore is None:
                self._ignore = False
            return self._ignore


class PathChecker(object):

    def __init__(self, path, args, label=None, logger=logging.getLogger('')):
        self.args = args
        self.ignore = ['*~', '*#', '*.swp', '*.py?', '*.o', '.git', '.svn']
        if self.args.exclude:
            self.ignore += self.args.exclude.split(',')
        self._read_gitignore()
        self.path = PathAttribute(path, ignore_patterns=self.ignore)
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
        if self.path.ignore:
            return False
        checks_passed = True
        for arg in args:
            checks_passed &= getattr(self.path, arg)
        return checks_passed

    def log_status(self, status, extra=''):
        if extra:
            extra = '(%s)' % extra
        if status == 'PASS':
            self.log.debug('%s: %s %s %s', self.label, self.path, status, extra)
        elif status == 'FAIL':
            self.log.error('%s: %s %s %s', self.label, self.path, status, extra)
