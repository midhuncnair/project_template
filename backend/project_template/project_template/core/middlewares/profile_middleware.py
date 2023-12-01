#! /usr/bin/env python3
"""
"""


# from __future__ import


__all__ = [
    'RequestTimeProfilerMiddleware',
    'RequestTimeProfilerMiddlewareASGI',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>"
]


import logging

from uuid import uuid4

from .constants import (
    REQUEST_ATTRS,
)
from .utils import (
    GathererUtil,
    add_request_record_to_db,
    add_request_record_to_db_async,
)

logger = logging.getLogger(__name__)


class RequestTimeProfilerMiddleware:
    """Adds the request_id for all the incoming requests
    generates profiling on request and adds the entry to the db.
    """
    def __init__(self, get_response):
        """
        initializes the get_response object
        so as to make it available
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        This gets called each time any
        request/response is being executed
        """
        # The functionality that are to be run before
        # request is being called
        if not hasattr(request, REQUEST_ATTRS[0]):
            request_id = uuid4().hex
            setattr(request, REQUEST_ATTRS[0], request_id)

        if not hasattr(request, REQUEST_ATTRS[1]):
            start_time = GathererUtil.time()
            setattr(request, REQUEST_ATTRS[1], start_time)

        response = self.get_response(request)
        # The functionality that are to be run after
        # request is being called
        if (
            not hasattr(request, REQUEST_ATTRS[0])
            or not hasattr(request, REQUEST_ATTRS[1])
        ):
            return response

        gu = GathererUtil(
            request=request,
            response_byte_size=len(response.content),
            response_reason_phrase=response.reason_phrase,
            response_status_code=getattr(response, 'status_code', 0)
        )
        gu.log
        add_request_record_to_db(gu.request_record)

        return response


class RequestTimeProfilerMiddlewareASGI:
    """Adds the request_id for all the incoming requests
    generates profiling on request and adds the entry to the db.
    """
    def __init__(self, inner):
        self.inner = inner

    async def wrap_send(self, scope, org_send):
        """
        """
        async def ret_send(*args, **kwargs):
            if (
                scope.get(REQUEST_ATTRS[0]) is not None
                and scope.get(REQUEST_ATTRS[1]) is not None
            ):
                logger.debug(
                    f"RequestTimeProfilerMiddlewareASGI: ret_send args = {args}, kwargs={kwargs}"
                )
                response_byte_size = 0 # need to compute from args/kwargs
                gu = GathererUtil(
                    scope=scope,
                    response_byte_size=response_byte_size,
                    response_reason_phrase=0,
                    response_status_code=0,
                )
                gu.log
                await add_request_record_to_db_async(gu.request_record)

            return await org_send(*args, **kwargs)

        return ret_send

    async def __call__(self, scope, receive, send):
        # Copy scope to stop changes going upstream
        scope = dict(scope)

        if scope.get(REQUEST_ATTRS[0]) is None:
            request_id = uuid4().hex
            scope[REQUEST_ATTRS[0]] = request_id

        if scope.get(REQUEST_ATTRS[1]) is None:
            start_time = GathererUtil.time()
            scope[REQUEST_ATTRS[1]] = start_time

        send = await self.wrap_send(scope, send)

        return await self.inner(scope, receive, send)
