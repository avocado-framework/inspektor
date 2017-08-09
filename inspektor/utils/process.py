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
import shlex
import subprocess
import time

from . import exceptions

log = logging.getLogger('inspektor.utils')


class CmdResult(object):

    """
    Command execution result.

    command:     String containing the command line itself
    exit_status: Integer exit code of the process
    stdout:      String containing stdout of the process
    stderr:      String containing stderr of the process
    duration:    Elapsed wall clock time running the process
    """

    def __init__(self, command="", stdout="", stderr="",
                 exit_status=None, duration=0):
        self.command = command
        self.exit_status = exit_status
        self.stdout = stdout
        self.stderr = stderr
        self.duration = duration

    def __repr__(self):
        return ("Command: %s\n"
                "Exit status: %s\n"
                "Duration: %s\n"
                "Stdout:\n%s\n"
                "Stderr:\n%s\n" % (self.command, self.exit_status,
                                   self.duration, self.stdout, self.stderr))


def run(cmd, verbose=True, ignore_status=False, shell=False):
    if verbose:
        log.info("Running '%s'", cmd)
    if shell is False:
        args = shlex.split(cmd)
    else:
        args = cmd
    start = time.time()
    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=shell)
    stdout, stderr = p.communicate()
    duration = time.time() - start
    result = CmdResult(cmd)
    result.exit_status = p.returncode
    result.stdout = str(stdout)
    result.stderr = str(stderr)
    result.duration = duration
    if p.returncode != 0 and not ignore_status:
        raise exceptions.CmdError(cmd, result)
    return result
