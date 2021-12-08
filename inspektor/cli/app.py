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
Implements the base inspektor application.
"""
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager


class InspektorApp(App):

    def __init__(self):
        super(InspektorApp, self).__init__(
            description='Inspektor python code checker and fixer',
            version='0.5.3',
            command_manager=CommandManager('inspektor.app'),
            deferred_help=True,
            )

    def clean_up(self, cmd, result, err):
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    inspekt = InspektorApp()
    try:
        return inspekt.run(argv)
    except KeyboardInterrupt:
        inspekt.LOG.error('User requested to interrupt')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
