import cli
import exceptions
import inspector
import lint
import reindent
import utils
import vcs

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


logging.config.dictConfig(DEFAULT_LOGGING)
