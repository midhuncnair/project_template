#! /usr/bin/env python3
"""
Defines the log settings
"""


# from __future__ import


__all__ = [
    "LOGS_DIR",
    "LOGGING",
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


import os

from .constants import BASE_DIR as __BASE_DIR
from .app_settings import (
    APPLICATION_VERSION_FULL as app_full_version
)

# Logging
LOGS_DIR = os.path.join(__BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [v" + app_full_version + "] [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'project_template_logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, "project_template.log"),
            'maxBytes': 2 * 1024 * 1024, # 2 mega.
            'backupCount': 7,
            'formatter': 'standard',
        },
        'django_related': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, "django_related.log"),
            'maxBytes': 2 * 1024 * 1024, # 2 mega.
            'backupCount': 7,
            'formatter': 'standard',
        },
        'other_logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, "other.log"),
            'maxBytes': 2 * 1024 * 1024, # 2 mega.
            'backupCount': 7,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'pytcolor.ColoredStreamHandler',
            'formatter': 'standard',
            'filters': ['require_debug_false'],
        },
        'console_debug': {
            'level': 'DEBUG',
            'class': 'pytcolor.ColoredStreamHandler',
            'formatter': 'standard',
            'filters': ['require_debug_true'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_related'],
            'level': 'WARN',
        },
        'project_template': {
            'handlers': ['console', 'console_debug', 'project_template_logfile'],
            'level': 'DEBUG',
        },
        '': {
            'handlers': ['other_logfile'],
            'level': 'DEBUG',
        }
    }
}
