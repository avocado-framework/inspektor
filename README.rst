Inspektor
=========

Inspektor is a program used to verify the code of your python project. It
evolved from a set of scripts used to check patch and code of python projects
of the autotest organization [1]. As the project grew and new modules started
to be developed, we noticed the same scripts had to be copied to each new
project repo, creating a massive headache when we needed to update said
scripts.

Inspektor knows how to:

1) Check code with the help of `pylint`.
2) Check indentation of your code, correcting it if necessary.
3) Check whether your code is PEP8 compliant, correcting it if necessary.
4) Run unittests inside your tree, provided they follow some conventions.
5) If your project is hosted on the autotest github area, it can apply pull
   requests made against it, and check if it introduced any regression from
   the metrics outlined above

This all assumes you're working on a version control checkout of your code.
Currently inspektor knows how to handle subversion and git.

Installing inspektor
--------------------

If there are no packages for your distro, you'll have to resort to good old:

::

    $ sudo python setup.py install

Fedora
~~~~~~

Fedora users lmr's COPR:

http://copr.fedoraproject.org/coprs/lmr/Autotest/

Add the COPR repository, which, just for reference, on a Fedora 20 could be done through:

::

    $ sudo curl http://copr.fedoraproject.org/coprs/lmr/Autotest/repo/fedora-20-i386/lmr-Autotest-fedora-20-i386.repo > /etc/yum.repos.d/autotest.repo

Users of Fedora 19 or Rawhide can use the other repo files available in the
COPR web page. Now you can install it using:

::

    $ sudo yum install inspektor

Ubuntu
~~~~~~

lmr's PPA:

https://launchpad.net/~lmr/+archive/autotest

Add the repos through the instructions on that page. Now you can install it
using:

::

    $ sudo apt-get install inspektor

Usage
-----

1) Go to the root of your project source code clone
2) If you want to check code with pylint:

::

    inspekt lint
3) If you want to check indentation:

::

    inspekt indent
4) If you want to check compliance to the PEP8:

::

    inspekt style
5) If you want to check PR #123 for a project inside the autotest github area:

::

    inspekt github 123

[1] http://autotest.github.io/
