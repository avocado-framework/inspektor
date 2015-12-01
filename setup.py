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
from setuptools import setup
import sys

if sys.version_info[:2] == (2, 6):
    REQUIRES = ['astroid==1.2.1', 'pep8>=1.6.2', 'pylint==1.3.1', 'logutils>=0.3.3']
else:
    REQUIRES = ['pep8>=1.6.2', 'pylint>=1.3']

setup(name='inspektor',
      version='0.1.19',
      description='Inspektor code checker',
      author='Lucas Meneghel Rodrigues',
      author_email='lmr@redhat.com',
      url='https://github.com/autotest/inspektor',
      packages=['inspektor',
                'inspektor.cli',
                'inspektor.utils'
                ],
      install_requires=REQUIRES,
      scripts=['scripts/inspekt'],
      )
