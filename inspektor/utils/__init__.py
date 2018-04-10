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
import random
import string

import six

from . import download
from . import process

# pylint: disable=E0602
if six.PY2:
    input = raw_input

log = logging.getLogger(__name__)


def ask(question, auto=False, options="y/n"):
    """
    Raw input with a prompt.

    :param question: Question to be asked
    :param auto: Whether to return "y" instead of asking the question
    """
    if auto:
        log.info("%s (%s) y", question, options)
        return "y"
    return input("%s (%s) ", question, options)


def random_string(length, ignore_str=string.punctuation,
                  convert_str=""):
    """
    Return a random string using alphanumeric characters.

    :param length: Length of the string that will be generated.
    :param ignore_str: Characters that will not include in generated string.
    :param convert_str: Characters that need to be escaped (prepend "\\").

    :return: The generated random string.
    """
    r = random.SystemRandom()
    result = ""
    chars = string.ascii_letters + string.digits + string.punctuation
    if not ignore_str:
        ignore_str = ""
    for i in ignore_str:
        chars = chars.replace(i, "")

    while length > 0:
        tmp = r.choice(chars)
        if convert_str and (tmp in convert_str):
            tmp = "\\%s" % tmp
        result += tmp
        length -= 1
    return str
