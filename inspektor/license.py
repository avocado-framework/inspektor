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

from .path import PathChecker


LICENSE_SNIPPET_GPLV2 = """# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
"""

LICENSE_SNIPPET_GPLV2_STRICT = """# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; specifically version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
"""

license_mapping = {'gplv2_later': LICENSE_SNIPPET_GPLV2,
                   'gplv2_strict': LICENSE_SNIPPET_GPLV2_STRICT}
default_license = 'gplv2_later'


class LicenseChecker(object):

    def __init__(self, args, logger=logging.getLogger('')):
        self.license_type = args.license
        cpyright = args.copyright
        author = args.author
        self.args = args
        self.failed_paths = []
        self.log = logger
        self.license_contents = license_mapping[self.license_type]
        self.base_license_contents = self.license_contents

        if cpyright:
            self.license_contents += "#\n"
            self.license_contents += "# " + cpyright + "\n"

        if author:
            self.license_contents += "# " + author + "\n"

    def check_dir(self, path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                self.check_file(os.path.join(root, filename))
        return not self.failed_paths

    def check_file(self, path):
        checker = PathChecker(path=path, args=self.args, label='License',
                              logger=self.log)
        # Don't put license info in empty __init__.py files.
        if not checker.check_attributes('text', 'python', 'not_empty'):
            return True

        first_line = None
        if checker.path.script('python'):
            first_line = checker.path.first_line

        with open(path, 'r') as inspected_file:
            content = inspected_file.readlines()
            if first_line is not None:
                content = content[1:]
            content = "".join(content)
            if self.base_license_contents not in content:
                fix_status = ''
                if self.args.fix:
                    new_content = ""
                    if first_line is not None:
                        new_content += first_line
                        new_content += '\n'
                    new_content += self.license_contents + '\n' + content
                    with open(path, 'w') as inspected_file:
                        inspected_file.write(new_content)
                        fix_status = 'FIX OK'

                self.failed_paths.append(path)
                checker.log_status(status='FAIL', extra=fix_status)
                return False
            else:
                checker.log_status(status='PASS')
                return True

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)
        else:
            self.log.error("Invalid location '%s'", path)
            return False
