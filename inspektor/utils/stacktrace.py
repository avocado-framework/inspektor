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

"""
Traceback standard module plus some additional APIs.
"""
import inspect
import logging
from traceback import format_exception


def tb_info(exc_info):
    """
    Prepare traceback info.

    :param exc_info: Exception info produced by sys.exc_info()
    """
    exc_type, exc_value, exc_traceback = exc_info
    return format_exception(exc_type, exc_value, exc_traceback.tb_next)


def prepare_exc_info(exc_info):
    """
    Prepare traceback info.

    :param exc_info: Exception info produced by sys.exc_info()
    """
    return "".join(tb_info(exc_info))


def log_exc_info(exc_info, logger='root'):
    """
    Log exception info to logger_name.

    :param exc_info: Exception info produced by sys.exc_info()
    :param logger: Name of the logger (defaults to root)
    """
    log = logging.getLogger(logger)
    log.error('')
    called_from = inspect.currentframe().f_back
    log.error("Reproduced traceback from: %s:%s",
              called_from.f_code.co_filename, called_from.f_lineno)
    for line in tb_info(exc_info):
        for l in line.splitlines():
            log.error(l)
    log.error('')


def log_message(message, logger='root'):
    """
    Log message to logger.

    :param message: Message
    :param logger: Name of the logger (defaults to root)
    """
    log = logging.getLogger(logger)
    for line in message.splitlines():
        log.error(line)
