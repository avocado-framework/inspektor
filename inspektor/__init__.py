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

import logging.config

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'brief': {
            'format': '%(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
        },
    },
    'loggers': {
        'inspektor': {
            'handlers': ['console'],
        },
        'inspektor.app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inspektor.lint': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inspektor.license': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inspektor.style': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inspektor.utils': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inspektor.check': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inspektor.reindent': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inspektor.vcs': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


from logging import config

if not hasattr(config, 'dictConfig'):
    from logutils import dictconfig
    cfg_func = dictconfig.dictConfig
else:
    cfg_func = config.dictConfig

cfg_func(DEFAULT_LOGGING)
