"""
This base for view permissions.
"""


# from __future__ import


__all__ = [
    'SuperUserPermission',
]
__version__ = "0.1.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


import logging

from rest_framework import (
    permissions,
)


logger = logging.getLogger(__name__)


class SuperUserPermission(permissions.BasePermission):
    """
    """

    def setup(self, request):
        """
        """

        self.user = request.user
        self.super_user = self.user.is_superuser
        self.admin = self.super_user

        return self.user.is_active


    def has_permission(self, request, view):
        """
        """
        status = self.setup(request)

        if not status:
            return False

        if self.super_user:
            return True

        return False
