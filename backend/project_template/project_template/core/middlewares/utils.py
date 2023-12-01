#! /usr/bin/env python3
"""
"""


# from __future__ import


__all__ = [
    'add_request_record_to_db',
    'add_request_record_to_db_async',
    'GathererUtil',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>"
]


import logging
import threading
import pytz

from datetime import datetime
from functools import cached_property
from channels.db import database_sync_to_async

from appmanagement.models import RequestTracker

from .constants import (
    ENVIRONMENT,
    REQUEST_ATTRS,
    REQUEST_LOG,
)


logger = logging.getLogger(__name__)



def __add_request_record_to_db(data):
    RequestTracker.objects.create(**data)

def add_request_record_to_db(request_data):
    if (
        request_data['user'] is not None
        and request_data['path'].find('/admin') == -1
    ):
        thread = threading.Thread(
            target=__add_request_record_to_db,
            args=(request_data,),
            kwargs={}
        )
        thread.daemon = True
        thread.start()


async def add_request_record_to_db_async(request_data):
    if (
        request_data['user'] is not None
        and request_data['path'].find('/admin') == -1
    ):
        database_sync_to_async(__add_request_record_to_db)(request_data)


class GathererUtil:
    def __init__(
        self, request=None, scope=None,
        response_byte_size=0, response_reason_phrase='',
        response_status_code=0,
    ):
        if request is None and scope is None:
            raise ValueError("GathererUtil: Both request and scope is None")
        elif request is not None and scope is not None:
            raise ValueError("GathererUtil: Both request and scope is not None")

        self.request = request
        self.scope = scope
        self.response_byte_size = response_byte_size
        self.response_reason_phrase = response_reason_phrase
        self.response_status_code = response_status_code

    @staticmethod
    def time():
        """Get utc format time.
        """
        if ENVIRONMENT == 'local':
            return datetime.now()
        return pytz.utc.localize(datetime.utcnow())

    @cached_property
    def is_request(self):
        if self.request is not None and self.scope is None:
            return True
        return False

    @cached_property
    def is_scope(self):
        if self.request is None and self.scope is not None:
            return True
        return False

    @cached_property
    def user(self):
        user = None
        try:
            if self.is_request:
                user = self.request.user
            elif self.is_scope:
                user = self.scope["user"]
            user_id = user.pk
            user_email = user.email
            user_name = user.userprofile.name
        except:  # noqa E722 Exception as err:
            user = None
            user_id = '?'
            user_email = '??'
            user_name = '??'

        return user, user_id, user_email, user_name

    @cached_property
    def request_id(self):
        if self.is_request:
            request_id = getattr(self.request, REQUEST_ATTRS[0])
        elif self.is_scope:
            request_id = self.scope[REQUEST_ATTRS[0]]
        return request_id

    @cached_property
    def start_time(self):
        if self.is_request:
            start_time = getattr(self.request, REQUEST_ATTRS[1])
        elif self.is_scope:
            start_time = self.scope[REQUEST_ATTRS[1]]
        return start_time

    @cached_property
    def end_time(self):
        return GathererUtil.time()

    @cached_property
    def request_path(self):
        if self.is_request:
            return self.request.get_full_path()

        return 'ws->scope'

    @cached_property
    def request_method(self):
        if self.is_request:
            return self.request.method.upper()

        return 'ws->scope'

    @cached_property
    def duration(self):
        return (self.end_time - self.start_time).total_seconds()*1000

    @cached_property
    def request_record(self):
        return {
            'request_id': self.request_id,
            'user': self.user[0],
            'path': self.request_path,
            'method': self.request_method,
            'status': self.response_status_code,
            'duration': self.duration,
            'byte_size': self.response_byte_size,
            'response_reason_phrase': self.response_reason_phrase,
        }

    @cached_property
    def log_line(self):
        """ Format the log line and returns
        """
        global REQUEST_LOG
        return REQUEST_LOG.format(
            request_id=self.request_id,
            url=self.request_path,
            method=self.request_method,
            status=self.response_status_code,
            delta=self.duration,
            t_unit='ms',
            size=self.response_byte_size,
            s_unit='b',
            reason=self.response_reason_phrase
        )

    @cached_property
    def log(self):
        logger.info(self.log_line)
