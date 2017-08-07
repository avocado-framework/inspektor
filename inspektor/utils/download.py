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
import shutil
import socket

import six

# pylint: disable=E0611
# pylint: disable=E1101
if six.PY2:
    import urllib2
    import urlparse
    _URL_PARSE = urlparse.urlparse
    _URL_OPEN = urllib2.urlopen
else:
    import urllib.request
    import urllib.parse
    _URL_PARSE = urllib.parse.urlparse
    _URL_OPEN = urllib.request.urlopen

log = logging.getLogger('inspektor.utils')


def is_url(path):
    """
    Return true if path looks like a URL
    """
    url_parts = _URL_PARSE(path)
    return url_parts[0] in ('http', 'https', 'ftp', 'git')


def url_open(url, data=None, timeout=5):
    """
    Wrapper to urllib2.urlopen with timeout addition.
    """
    # Save old timeout
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        return _URL_OPEN(url, data=data)
    finally:
        socket.setdefaulttimeout(old_timeout)


def url_download(url, filename, data=None, timeout=300):
    """
    Retrieve a file from given url.
    """
    log.info('Fetching %s -> %s', url, filename)

    src_file = url_open(url, data=data, timeout=timeout)
    try:
        dest_file = open(filename, 'wb')
        try:
            shutil.copyfileobj(src_file, dest_file)
        finally:
            dest_file.close()
    finally:
        src_file.close()


def get_file(src, dest, permissions=None):
    """
    Get a file from src, which can be local or a remote URL
    """
    if src == dest:
        return

    if is_url(src):
        url_download(src, dest)
    else:
        shutil.copyfile(src, dest)

    if permissions:
        os.chmod(dest, permissions)
    return dest
