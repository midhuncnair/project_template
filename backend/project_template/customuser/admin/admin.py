"""
The admin page settings for customuser module
"""


# from __future__ import


__all__ = [
    'UserProfileAdmin',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


import logging

from django.contrib import admin
from project_template.base import BaseModelAdmin

from customuser.models import (
    UserProfile,
    ForgotPasswordRequests,
)

logger = logging.getLogger(__name__)


class UserProfileAdmin(BaseModelAdmin):
    def user_id(self, obj):
        return obj.user.pk

    def username(self, obj):
        return obj.user.username

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    list_display = ('pk', 'username', 'user_id', 'first_name', 'last_name', 'initials', 'password_status', 'password_version')
    list_display_links = ('pk', 'username')
    search_fields = ('user__username', )
    list_filter = ('password_status',)


class ForgotPasswordRequestsAdmin(BaseModelAdmin):
    list_display = ('pk', 'user', 'request_id', 'is_satisfied', 'is_expired', 'is_valid')


admin.site.register(ForgotPasswordRequests, ForgotPasswordRequestsAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
