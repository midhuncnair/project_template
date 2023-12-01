"""
The admin page settings for appmanagement module
"""


# from __future__ import


__all__ = [
    'AppReleaseAdmin',
    'RequestTracker',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


import logging

from django.contrib import admin
from project_template.base import BaseModelAdmin

from appmanagement.models import (
    AppRelease,
    RequestTracker,
)

logger = logging.getLogger(__name__)


class AppReleaseAdmin(BaseModelAdmin):
    list_display = (
        'app_release_id',
        'name',
        'version_fe',
        'version_be',
        'created_by',
        'updated_by',
        'status_fe',
        'status_be',
        # 'milestone_fe',
        # 'milestone_be',
    )
    list_display_links = ('app_release_id', 'name')
    search_fields = ('name', )
    list_filter = ('version_fe', 'version_be', 'status_fe', 'status_be')


class RequestTrackerAdmin(BaseModelAdmin):
    list_display = (
        'request_id',
        'user',
        'path',
        'method',
        'status',
        'duration',
        'byte_size',
        'response_reason_phrase',
    )
    list_display_links = ('request_id', 'user')
    search_fields = ('user__email', 'user__username')
    list_filter = ('status',)


admin.site.register(RequestTracker, RequestTrackerAdmin)
admin.site.register(AppRelease, AppReleaseAdmin)
