"""
This module define all the custom user related
permissions.
"""


# from __future__ import


# __all__ = []
__version__ = "0.1.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


import logging

from rest_framework import (
    permissions,
)
from project_template.base import SuperUserPermission


logger = logging.getLogger(__name__)


class UserBasePermission(SuperUserPermission):
    """
    This will define the base permission set that we are
    looking for in each request.
    """

    def setup(self, request):
        """
        This will do all the basic setup, that are
        needed for permission checking
        """
        status = super().setup(request)
        return status

    def has_permission(self, request, view):
        """
        Overrides the default has_permission of BasePermission class.
        """
        print("In user base permission")
        status = self.setup(request)

        if not status:
            return False

        if self.admin:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """
        Overrides the default has_object_permission of BasePermission class.
        """
        print("In user base permission has_object_permission", view, obj)
        status = self.setup(request)

        if not status:
            return False

        if self.admin:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return super().has_object_permission(request, view, obj)
