from distutils.core import setup

import inspektor.version

setup(name='inspektor',
      version=inspektor.version.VERSION,
      description='Inspektor code checker',
      author='Lucas Meneghel Rodrigues',
      author_email='lmr@redhat.com',
      url='http://autotest.github.com',
      packages=['inspektor',
                'inspektor.cli',
                'inspektor.utils'
                ],
      scripts=['scripts/inspekt'])
