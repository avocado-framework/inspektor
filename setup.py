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

from distutils.core import setup

setup(name='inspektor',
      version='0.1.14',
      description='Inspektor code checker',
      author='Lucas Meneghel Rodrigues',
      author_email='lmr@redhat.com',
      url='https://github.com/autotest/inspektor',
      packages=['inspektor',
                'inspektor.cli',
                'inspektor.utils'
                ],
      install_requires=['pylint>=1.3.0',
                        'autopep8>=1.0.0'],
      scripts=['scripts/inspekt'],
      )
