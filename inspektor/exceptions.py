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
