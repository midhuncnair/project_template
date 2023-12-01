#! /usr/bin/env python3
"""
"""


# from __future__ import


__all__ = [
    'ExceptionMiddleware',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>"
]


import logging
import traceback

from hashlib import md5

from django.http import (
    JsonResponse,
)
from project_template.request_utils.context import (
    set_current_context,
)
# from project_template.project_template.request_utils.context import (
#     set_current_context,
# )

logging = logging.getLogger(__name__)


class ExceptionMiddleware:
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
        response = self.get_response(request)
        return response

    def process_view(self, request, view_function, view_args, view_kwargs):
        """
        This will be called before calling the view, so here we can add
        necessary things to request for using it in permission.
        """
        request.view_args = view_args
        request.view_kwargs = view_kwargs
        return

    def process_exception(self, request, exception):
        """
        Handles the exception logging
        """
        traceback_str = traceback.format_exc()
        exception_str = str(exception)
        request_id = request._request_id

        md5_obj = md5()
        md5_obj.update(exception_str.encode('utf-8'))
        error_id = md5_obj.hexdigest()

        logging.error(
            f"{exception.__class__.__name__}:{exception_str}\nError ({error_id})\n"
            + f"Traceback*****-->\n(\n{traceback_str})\n<--****Request:{request_id}"
        )

        payload = {
            "error": f"Error ({error_id}): Try Again, or Contact us!",
            "request_id": request_id,
            "error_id": error_id,
            "error_text": f"Exception\n(\n{exception_str}\n)\nTracebace\n(\n{traceback_str}\n)\n"
        }

        set_current_context(request_id=None)

        return JsonResponse(payload, status=500)

    # def process_template_response(self, request, response):
    #     """
    #     """
    #     return response


