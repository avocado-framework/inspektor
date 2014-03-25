"""
Implements the base inspektor application.
"""
import logging
from argparse import ArgumentParser

from inspektor import lint
from inspektor import reindent
from inspektor import style
from inspektor import check

log = logging.getLogger("inspektor.app")


class InspektorApp(object):

    """
    Basic inspektor application.
    """

    def __init__(self):
        self.arg_parser = ArgumentParser(description='Inspektor code check')
        self.arg_parser.add_argument('-v', '--verbose', action='store_true',
                                     help='print extra debug messages',
                                     dest='verbose')

        subparsers = self.arg_parser.add_subparsers(title='subcommands',
                                                    description='valid subcommands',
                                                    help='subcommand help')
        lint.set_arguments(subparsers)
        reindent.set_arguments(subparsers)
        style.set_arguments(subparsers)
        check.set_arguments(subparsers)
        self.args = self.arg_parser.parse_args()

    def run(self):
        return self.args.func(self.args)
