Inspektor
=========

Inspektor is a program used to verify the code of your python project. It
evolved from a set of scripts used to check patch and code of python projects
of the autotest organization [1]. As the project grew and new modules started
to be developed, we noticed the same scripts had to be copied to each new
project repo, creating a massive headache when we needed to update said
scripts.

Inspektor is supposed to be installed system wide, using the standard:

::

    python setup.py install


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

Usage
-----

1) Go to the root of your project source code clone
2) If you want to check code with pylint:
::

    inspekt lint
3) If you want to check indentation:
::

    inspekt indent

[1] http://autotest.github.io/
