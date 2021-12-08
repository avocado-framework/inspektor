Inspektor
=========

Inspektor is a program used to verify the code of your python project. It
evolved from a set of scripts used to check patches and code of python projects
of the autotest organization [1]. As the project grew and new modules started
to be developed, we noticed the same scripts had to be copied to each new
project repo, creating a massive headache when we needed to update said
scripts.

Inspektor knows how to:

1) Check code with the help of `pylint`.
2) Check indentation of your code with the help of `pycodestyle`,
   correcting it if you so deem appropriate.
3) Check whether your code is PEP8 compliant, correcting it if necessary
   (only works if you have `autopep8` installed) if you so deem appropriate.
4) If your project is hosted on the autotest github area, it can apply pull
   requests made against it, and check if it introduced any regression from
   the metrics outlined above.

This all assumes you're working on a version control checkout of your code.
Currently inspektor knows how to handle subversion and git.

Installing inspektor
--------------------

You can get inspektor through pip:

::

    $ sudo pip install inspektor

But you should avoid doing that if possible. A virtual environment deployment
tends to be better, since each installation is restricted to each environment:

::

    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install inspektor

If you are developing inspektor, you can install it in your virtual environment
as an editable package. From this source code tree root:

::

    $ pip install -e .

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
