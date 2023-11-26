#! /usr/bin/env python
"""application related settings
"""


__all__ = [
    "APPLICATION_VERSION_FULL",
    "UPLOAD_DIR",
    "CHAR_FIELD_LENGTH",
    "SHORT_CHAR_FIELD_LENGTH",
    "BIG_CHAR_FIELD_LENGTH",
    "ALLOWED_CHARS",
    "EXPIRATION_TIME",
    "USER_SECRET_LENGTH",
    "USER_SECRET_VERSION_LENGTH",
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import os
from .constants import BASE_DIR


# Build Settings
#     TODO: add the build related settigns here (version details)
APPLICATION_VERSION_FULL = os.environ.get("FULL_VERSION", '1.0.0.0')


# shared folder details for apps to run
UPLOAD_DIR = os.path.join(BASE_DIR, "Upload_Manager", "temp_upld_folder")


# FIELD SETTINGS
CHAR_FIELD_LENGTH = 50
SHORT_CHAR_FIELD_LENGTH = 25
BIG_CHAR_FIELD_LENGTH = 256
ALLOWED_CHARS = r'([^A-Za-z0-9._])'


# Resource Expiration time (in days)
EXPIRATION_TIME = 30

# User Settings
USER_SECRET_LENGTH = 8
USER_SECRET_VERSION_LENGTH = 2
