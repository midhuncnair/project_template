#! /usr/bin/env python3
"""
"""


# from __future__ import


__all__ = [
    'get_request_tracker',
    'get_current_context',
    'set_current_context',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>"
]


import logging
import threading

from appmanagement.models import RequestTracker


logger = logging.getLogger(__name__)
_thread_local = threading.local()


def get_request_tracker(request_id):
    c_request = RequestTracker.objects.get(request_id=request_id)
    return c_request


def get_current_context():
    return getattr(_thread_local, 'current_request', None)


def set_current_context(request_id=None):
    setattr(_thread_local, 'current_request', request_id)
