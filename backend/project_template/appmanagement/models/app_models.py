"""
This module contains the models for core appManagement
"""

# from __future__ import


__all__ = [
    'AppRelease',
    'RequestTracker',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


import logging

from functools import cached_property
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import (
    get_user_model,
)
from project_template.base import (
    BaseAuditData,
    BaseManager,
    get_sentinel_user,
)
from appmanagement.utility import (
    gather_migration_files,
)


User = get_user_model()
logger = logging.getLogger(__name__)


class AppRelease(BaseAuditData):
    """Records the release cycle of application.
    """
    status_choice_fields = (
        (0, 'SUCCESS'),
        (1, 'ERROR'),
    )
    milestone_choice_fields = (
        (0, 'PENDING'),
        (1, 'BUILD'),
        (2, 'PUSH'),
        (3, 'DEPLOY'),
    )

    app_release_id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=settings.CHAR_FIELD_LENGTH,
        help_text="This will help to identify the purpose of the release. (build scripts can pass in branch name.)"
    )
    version_fe = models.CharField(
        max_length=settings.SHORT_CHAR_FIELD_LENGTH,
        help_text="This is the version of this release major.minor.revision.build",
    )
    version_be = models.CharField(
        max_length=settings.SHORT_CHAR_FIELD_LENGTH,
        help_text="This is the version of this release major.minor.revision.build",
    )
    migrations = models.JSONField(default=dict)
    created_by = models.ForeignKey(
        User,
        related_name='AppReleaseCreatedBy',
        on_delete=models.SET(get_sentinel_user),
        help_text="The user who created this version",
    )
    updated_by = models.ForeignKey(
        User,
        related_name='AppReleaseUpdatedBy',
        on_delete=models.SET(get_sentinel_user),
        help_text="The user who created this version",
        null=True,
        blank=True,
    )
    remarks = models.TextField(
        help_text="Add any remarks here."
    )

    status_fe = models.PositiveSmallIntegerField(
        default=0,
        choices=status_choice_fields,
    )
    status_be = models.PositiveSmallIntegerField(
        default=0,
        choices=status_choice_fields,
    )
    milestone_fe = models.PositiveSmallIntegerField(
        default=0,
        choices=milestone_choice_fields,
    )
    milestone_be = models.PositiveSmallIntegerField(
        default=0,
        choices=milestone_choice_fields,
    )

    objects = BaseManager()
    raw_objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['version_be', 'version_fe'],
                condition=Q(is_active=True),
                name='unique active app version'
            ),
            models.UniqueConstraint(
                fields=['name'],
                condition=Q(is_active=True),
                name='unique active app name'
            ),
        ]

    @cached_property
    def latest_release(self):
        return AppRelease.get_latest_release()

    @staticmethod
    def get_latest_release():
        latest_release = AppRelease.objects.filter(
            status_fe=0,
            status_be=0,
            milestone_fe=3,
            milestone_be=3,
        ).order_by('pk').last()

        return latest_release

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.remarks = 'Created by %s(%s)\n' % (
                self.created_by.userprofile.name,
                self.created_by
            )

            if not self.migrations:
                self.migrations = {
                    'start': gather_migration_files(),
                    'end': {}
                }

            if not self.version_be and not self.version_fe:
                raise ValueError("Both frontend and backend version cannot be empty.")
            elif not self.version_be or not self.version_fe:
                prev_release = self.latest_release
                if not self.version_be:
                    self.version_be = prev_release.version_be
                    self.status_be = prev_release.status_be
                    self.milestone_be = prev_release.milestone_be
                if not self.version_fe:
                    self.version_fe = prev_release.version_fe
                    self.status_fe = prev_release.status_fe
                    self.milestone_fe = prev_release.milestone_fe

        super().save(*args, **kwargs)


class RequestTracker(models.Model):
    request_id = models.UUIDField(primary_key=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET(get_sentinel_user),
        help_text="The user who made this request",
    )
    path = models.CharField(max_length=settings.BIG_CHAR_FIELD_LENGTH)
    method = models.CharField(max_length=settings.SHORT_CHAR_FIELD_LENGTH)
    status = models.PositiveIntegerField()
    duration = models.IntegerField()
    byte_size = models.PositiveIntegerField()
    response_reason_phrase = models.TextField()
    context = models.JSONField(default=dict)

    time_created = models.DateTimeField(
        default=timezone.now
    )
    time_updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    raw_objects = models.Manager()

    @cached_property
    def username(self):
        return self.user.username
