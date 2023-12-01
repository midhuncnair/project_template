#! /usr/bin/env python
"""context middlewares for request_utils
"""


# __all__ = []
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from ..context import (
    get_current_context,
    set_current_context,
)

from project_template.core.middlewares.constants import (
    REQUEST_ATTRS,
)


class ContextMiddleware:
    """Adds/removes context object to/from thread local
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """retrieves request_id from request that was set by RequestTimeProfilerMiddleware
        and sets it to thread local for all the processes to read and removes on the way out.
        """

        # set the request id to threadlocal
        request_id = getattr(request, REQUEST_ATTRS[0])
        set_current_context(request_id=request_id)

        response = self.get_response(request)

        # resset the request id from threadlocal
        set_current_context(request_id=None)

        return response

class ContextMiddlewareASGI:  # doubts the proper working of this
    """Adds/removes context object to/from thread local
    """
    def __init__(self, inner):
        self.inner = inner

    async def wrap_send(self, scope, org_send):
        """
        """
        async def ret_send(*args, **kwargs):
            set_current_context(request_id=None)
            return await org_send(*args, **kwargs)

        return ret_send

    async def __call__(self, scope, receive, send):
        # Copy scope to stop changes going upstream
        scope = dict(scope)

        request_id = scope.get(REQUEST_ATTRS[0])
        set_current_context(request_id=request_id)

        send = await self.wrap_send(scope, send)

        return await self.inner(scope, receive, send)
