#! /usr/bin/env python
"""Base Models
"""


__all__ = [
    "get_sentinel_user",
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import logging

from django.contrib.auth import (
    get_user_model,
)


logger = logging.getLogger(__name__)


def get_sentinel_user():
    """This is used to add a user when the user itself is deleted for asset management.
    """
    return get_user_model().objects.get_or_create(username='deleted')[0]
