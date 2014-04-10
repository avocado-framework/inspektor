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
Base exception definitions.
"""


class CmdError(Exception):

    def __init__(self, command, result):
        self.command = command
        self.result = result

    def __str__(self):
        if self.result.exit_status is None:
            msg = "Command '%s' failed and is not responding to signals"
            msg %= self.command
        else:
            msg = "Command '%s' failed (rc=%d)"
            msg %= (self.command, self.result.exit_status)
        return msg
