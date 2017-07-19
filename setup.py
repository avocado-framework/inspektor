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

# pylint: disable=E0611
import sys
from setuptools import setup, find_packages

PROJECT = 'inspektor'

# Change docs/sphinx/conf.py too!
VERSION = '0.4.0'

REQUIRES = ['six', 'cliff']
if sys.version_info[:2] == (2, 6):
    REQUIRES += ['astroid==1.2.1', 'pycodestyle>=2.0.0', 'pylint==1.3.1', 'logutils>=0.3.3']
elif sys.version_info[:2] == (2, 7):
    REQUIRES += ['pycodestyle>=2.0.0', 'pylint>=1.3']
elif sys.version_info[0] == 3:
    REQUIRES += ['pycodestyle', 'pylint']

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Inspektor python code checker and fixer',
    long_description=long_description,

    author='Lucas Meneghel Rodrigues',
    author_email='lookkas@gmail.com',

    url='https://github.com/avocado-framework/inspektor',
    download_url='https://github.com/avocado-framework/inspektor/tarball/master',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: GNU Public License 2',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=REQUIRES,

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'inspekt = inspektor.cli.app:main'
        ],
        'inspektor.app': [
            'lint = inspektor.lint:LintCommand',
            'indent = inspektor.reindent:ReindentCommand',
            'style = inspektor.style:StyleCommand',
            'github = inspektor.check:GithubCommand',
            'license = inspektor.license:LicenseCommand',
        ],
    },

    zip_safe=False,
)
