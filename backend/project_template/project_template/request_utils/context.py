#! /usr/bin/env python3
"""
"""


# from __future__ import


__all__ = [
    'get_current_context',
    'set_current_context',
    'DummyContext',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>"
]


# from django.dispatch import Signal, receiver


import logging
import threading


logger = logging.getLogger(__name__)
_thread_local = threading.local()


def get_current_context():
    """
    """
    return getattr(_thread_local, 'current_request', None)


def set_current_context(request=None):
    """
    """
    setattr(_thread_local, 'current_request', request)


class DummyContext:
    def __init__(self, request):
        self.actual_request = request

    @property
    def user(self):
        logger.critical(
            "\nDummyContext.user: This is not supposed to be called the request is already served\n"
        )
        return self.actual_request.user

    @property
    def request_context(self):
        logger.critical(
            "\nDummyContext.request_context:This is not supposed to be called the request is already served\n"
        )
        return self.actual_request.request_context

    def __getattr__(self, key):
        """
        """
        logger.critical(
            f"\nDummyContext.{key}: This is not supposed to be called the request is already served\n"
        )
        return getattr(self.actual_request, key)
