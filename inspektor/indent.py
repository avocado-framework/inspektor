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
import tokenize

import six

from .path import PathChecker
from .utils import stacktrace


def _rstrip(line, JUNK='\n \t'):
    """
    Return line stripped of trailing spaces, tabs, newlines.

    Note that line.rstrip() instead also strips sundry control characters,
    but at least one known Emacs user expects to keep junk like that, not
    mentioning Barry by name or anything <wink>.
    """

    i = len(line)
    while i > 0 and line[i - 1] in JUNK:
        i -= 1
    return line[:i]


def _getlspace(line):
    i, n = 0, len(line)
    while i < n and line[i] == " ":
        i += 1
    return i


class Run(object):

    def __init__(self, f):
        self.find_stmt = 1  # next token begins a fresh stmt?
        self.level = 0      # current indent level
        # Raw file lines.
        self.raw = f.readlines()
        f.close()

        # File lines, rstripped & tab-expanded.  Dummy at start is so
        # that we can use tokenize's 1-based line numbering easily.
        # Note that a line is all-blank iff it's "\n".
        self.lines = [_rstrip(line).expandtabs() + "\n"
                      for line in self.raw]
        self.lines.insert(0, None)
        self.index = 1  # index into self.lines of next line

        # List of (lineno, indentlevel) pairs, one for each stmt and
        # comment line.  indentlevel is -1 for comment lines, as a
        # signal that tokenize doesn't know what to do about them;
        # indeed, they're our headache!
        self.stats = []

    def run(self):
        # pylint: disable=E1121
        if six.PY2:
            tokenize.tokenize(self.getline, self.tokeneater)
        else:
            tokens = tokenize.generate_tokens(self.getline)
            for _token in tokens:
                self.tokeneater(*_token)
        # Remove trailing empty lines.
        lines = self.lines
        while lines and lines[-1] == "\n":
            lines.pop()
        # Sentinel.
        stats = self.stats
        stats.append((len(lines), 0))
        # Map count of leading spaces to # we want.
        have2want = {}
        # Program after transformation.
        after = self.after = []
        # Copy over initial empty lines -- there's nothing to do until
        # we see a line with *something* on it.
        i = stats[0][0]
        after.extend(lines[1:i])
        for i in range(len(stats) - 1):
            thisstmt, thislevel = stats[i]
            nextstmt = stats[i + 1][0]
            have = _getlspace(lines[thisstmt])
            want = thislevel * 4
            if want < 0:
                # A comment line.
                if have:
                    # An indented comment line.  If we saw the same
                    # indentation before, reuse what it most recently
                    # mapped to.
                    want = have2want.get(have, -1)
                    if want < 0:
                        # Then it probably belongs to the next real stmt.
                        for j in range(i + 1, len(stats) - 1):
                            jline, jlevel = stats[j]
                            if jlevel >= 0:
                                if have == _getlspace(lines[jline]):
                                    want = jlevel * 4
                                break
                    if want < 0:
                        for j in range(i - 1, -1, -1):
                            jline, jlevel = stats[j]
                            if jlevel >= 0:
                                want = have + _getlspace(after[jline - 1]) - \
                                    _getlspace(lines[jline])
                                break
                    if want < 0:
                        # Still no luck -- leave it alone.
                        want = have
                else:
                    want = 0
            assert want >= 0
            have2want[have] = want
            diff = want - have
            if diff == 0 or have == 0:
                after.extend(lines[thisstmt:nextstmt])
            else:
                for line in lines[thisstmt:nextstmt]:
                    if diff > 0:
                        if line == "\n":
                            after.append(line)
                        else:
                            after.append(" " * diff + line)
                    else:
                        remove = min(_getlspace(line), -diff)
                        after.append(line[remove:])
        return self.raw != self.after

    def write(self, f):
        f.writelines(self.after)

    # Line-getter for tokenize.
    def getline(self):
        if self.index >= len(self.lines):
            line = ""
        else:
            line = self.lines[self.index]
            self.index += 1
        return line

    # Line-eater for tokenize.
    def tokeneater(self, t_type, token, sline_scol, end, line,
                   INDENT=tokenize.INDENT,
                   DEDENT=tokenize.DEDENT,
                   NEWLINE=tokenize.NEWLINE,
                   COMMENT=tokenize.COMMENT,
                   NL=tokenize.NL):

        if t_type == NEWLINE:
            # A program statement, or ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            self.find_stmt = 1

        elif t_type == INDENT:
            self.find_stmt = 1
            self.level += 1

        elif t_type == DEDENT:
            self.find_stmt = 1
            self.level -= 1

        elif t_type == COMMENT:
            if self.find_stmt:
                sline, _ = sline_scol
                self.stats.append((sline, -1))
                # but we're still looking for a new stmt, so leave
                # find_stmt alone

        elif t_type == NL:
            pass

        elif self.find_stmt:
            # This is the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, or an
            # ENDMARKER.
            self.find_stmt = 0
            if line:   # not endmarker
                sline, _ = sline_scol
                self.stats.append((sline, self.level))


class Reindenter(object):

    def __init__(self, args, logger=logging.getLogger('')):
        self.args = args
        self.failed_paths = []
        self.log = logger

    def check_file(self, path):
        """
        Check one regular file for indentation errors.

        :param path: Path to a regular file.
        :return: False, if reindenter found problems, True, if reindenter
                 didn't find problems, path is not a python module or
                 script.
        """
        checker = PathChecker(path=path, args=self.args, label='Indent',
                              logger=self.log)
        if not checker.check_attributes('text', 'python', 'not_empty'):
            return True

        f = open(path)
        r = Run(f)
        f.close()
        try:
            if r.run():
                self.failed_paths.append(path)
                fix_status = ''
                if self.args.fix:
                    f = open(path, "w")
                    r.write(f)
                    f.close()
                    fix_status = 'FIX OK'
                checker.log_status(status='FAIL', extra=fix_status)
                return False
            else:
                checker.log_status(status='PASS')
                return True
        except IndentationError:
            self.log.error("Indentation check fail  : %s", path)
            self.log.error("Automated fix impossible: %s", path)
            self.log.error("Look at the stack trace "
                           "below and fix it manually")
            exc_info = sys.exc_info()
            stacktrace.log_exc_info(exc_info, 'inspektor.reindent')
            return False

    def check_dir(self, path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                self.check_file(os.path.join(root, filename))
        return not self.failed_paths

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)
        else:
            self.log.warning("Invalid location '%s'", path)
            return False
