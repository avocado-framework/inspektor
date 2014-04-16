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
from inspector import PathInspector

log = logging.getLogger("inspektor.license")

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

    def __init__(self, license_type=default_license, cpyright="", author=""):
        self.failed_paths = []

        self.license_contents = license_mapping[license_type]
        self.base_license_contents = self.license_contents

        if cpyright:
            self.license_contents += "#\n"
            self.license_contents += "# " + cpyright + "\n"

        if author:
            self.license_contents += "# " + author + "\n"

    def check_dir(self, path):
        def visit(arg, dirname, filenames):
            for filename in filenames:
                self.check_file(os.path.join(dirname, filename))

        os.path.walk(path, visit, None)
        return not self.failed_paths

    def check_file(self, path):
        inspector = PathInspector(path)
        # Don't put license info in empty __init__.py files.
        if not inspector.is_python() or inspector.is_empty():
            return True

        first_line = None
        if inspector.is_script("python"):
            first_line = inspector.get_first_line()

        new_content = None
        with open(path, 'r') as inspected_file:
            content = inspected_file.readlines()
            if first_line is not None:
                content = content[1:]
            content = "".join(content)
            if not self.base_license_contents in content:
                new_content = ""
                if first_line is not None:
                    new_content += first_line
                    new_content += '\n'
                new_content += self.license_contents + '\n' + content

        if new_content is not None:
            with open(path, 'w') as inspected_file:
                inspected_file.write(new_content)
                self.failed_paths.append(path)
                return False

        return True

    def check(self, path):
        if os.path.isfile(path):
            return self.check_file(path)
        elif os.path.isdir(path):
            return self.check_dir(path)


def set_arguments(parser):
    plicense = parser.add_parser('license',
                                 help='check for presence of license files')
    plicense.add_argument('path', type=str,
                          help='Path to check (empty for full tree check)',
                          nargs='?',
                          default="")
    plicense.add_argument('--license', type=str,
                          help=('License type. Supported license types: %s. '
                                'Default: %s' %
                                (license_mapping.keys(), default_license)),
                          default="gplv2_later")
    plicense.add_argument('--copyright', type=str,
                          help='Copyright string. Ex: "Copyright (c) 2013-2014 FooCorp"',
                          default="")
    plicense.add_argument('--author', type=str,
                          help='Author string. Ex: "Author: Brandon Lindon <brandon.lindon@foocorp.com>"',
                          default="")
    plicense.set_defaults(func=run_license)


def run_license(args):
    path = args.path
    license_type = args.license
    cpyright = args.copyright
    author = args.author

    if not path:
        path = os.getcwd()

    checker = LicenseChecker(license_type=license_type,
                             cpyright=cpyright, author=author)

    if checker.check(path):
        log.info("License check PASS")
        return 0
    else:
        log.error("License check FAIL")
        return 1
