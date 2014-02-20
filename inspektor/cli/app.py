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

        plint = subparsers.add_parser('lint', help='check code with pylint')
        plint.add_argument('path', type=str,
                           help='Path to check (empty for full tree check)',
                           nargs='?',
                           default="")
        plint.set_defaults(func=lint.run_lint)

        pindent = subparsers.add_parser('indent', help='check code indentation')
        pindent.add_argument('path', type=str,
                             help='Path to check (empty for full tree check)',
                             nargs='?',
                             default="")
        pindent.set_defaults(func=reindent.run_reindent)

        pstyle = subparsers.add_parser('style',
                                       help='check code compliance to PEP8')
        pstyle.add_argument('path', type=str,
                            help='Path to check (empty for full tree check)',
                            nargs='?',
                            default="")
        pstyle.set_defaults(func=style.run_style)

        pgh = subparsers.add_parser('github',
                                    help='check GitHub Pull Requests')
        pgh.add_argument('gh_id', type=int,
                         help='GitHub Pull Request ID')
        pgh.set_defaults(func=check.check_patch_github)

        self.args = self.arg_parser.parse_args()

    def run(self):
        self.args.func(self.args)
