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

import logging
import os

from cliff.command import Command

from inspektor import utils
from inspektor.patch import PatchChecker


class GithubPatchChecker(PatchChecker):

    def __init__(self, args, patch=None, logger=logging.getLogger('')):
        super(GithubPatchChecker, self).__init__(args=args, patch=patch,
                                                 logger=logger)
        self.github_id = args.gh_id
        self.github_parent_project = args.parent_project
        assert self.github_id is not None
        assert self.github_parent_project is not None
        self.patch = self._fetch_from_github()

    def _get_github_repo_name(self):
        return self.vcs.get_repo_name()

    def _get_github_url(self):
        """
        Gets the correct github URL for the given project.
        """
        repo = self._get_github_repo_name()
        return ("https://github.com/%s/%s/pull/%s.patch" %
                (self.github_parent_project, repo, self.github_id))

    def _fetch_from_github(self):
        """
        Gets a patch file from patchwork and puts it under the base dir.

        :param gh_id: Patchwork patch id.
        """
        patch_url = self._get_github_url()
        patch_dest = os.path.join(self.base_dir,
                                  'github-%s.patch' % self.github_id)
        return utils.download.get_file(patch_url, patch_dest)

    def check(self):
        self.vcs.apply_patch(self.patch)
        passed_check = self.check_modified_files()
        if passed_check:
            self.log.info('Github PR %s check PASS', self.github_id)
            return 0
        else:
            self.log.error('Github PR %s check FAIL', self.github_id)
            return 1


class GithubCommand(Command):
    """
    check github pull requests
    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(GithubCommand, self).get_parser(prog_name)
        parser.add_argument('gh_id', type=int,
                            help='GitHub Pull Request ID')
        parser.add_argument('-p', '--parent-project', type=str,
                            help=('Github organization. '
                                  'Default: %(default)s'),
                            default='avocado-framework')
        parser.add_argument('--disable', type=str,
                            help='Disable the pylint errors. Default: %(default)s',
                            default='W,R,C,E1002,E1101,E1103,E1120,F0401,I0011')
        parser.add_argument('--enable', type=str,
                            help=('Enable the pylint errors '
                                  '(takes place after disabled items are '
                                  'processed). Default: %(default)s'),
                            default='W0611')
        parser.add_argument('--pep8-disable', type=str,
                            help='Disable the pep8 errors. Default: %(default)s',
                            default='E501,E265,W601,E402')
        parser.add_argument('--exclude', type=str,
                            help='Quoted string containing paths or '
                                 'patterns to be excluded from '
                                 'checking, comma separated')
        return parser

    def take_action(self, parsed_args):
        checker = GithubPatchChecker(parsed_args, logger=self.log)
        checker.validate()
        return checker.check()
