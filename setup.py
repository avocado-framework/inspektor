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
    REQUIRES = ['astroid==1.2.1', 'pycodestyle>=2.0.0', 'pylint==1.3.1', 'logutils>=0.3.3']
elif sys.version_info[:2] == (2, 7):
    REQUIRES = ['pycodestyle>=2.0.0', 'pylint>=1.3']
elif sys.version_info[0] == 3:
    REQUIRES = ['pycodestyle', 'pylint']


setup(name='inspektor',
      version='0.3.0',
      description='Inspektor code checker',
      author='Lucas Meneghel Rodrigues',
      author_email='lookkas@gmail.com',
      url='https://github.com/avocado-framework/inspektor',
      packages=['inspektor',
                'inspektor.cli',
                'inspektor.utils'
                ],
      install_requires=REQUIRES,
      scripts=['scripts/inspekt'],
      )
