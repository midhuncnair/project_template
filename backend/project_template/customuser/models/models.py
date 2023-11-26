#! /usr/bin/env python
"""Models for customuser app
"""


__all__ = [
    'UserProfile',
    'ForgotPasswordRequests',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import pytz

from uuid import uuid4
from datetime import datetime, timedelta

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property

from project_template.base import BaseAuditData, BaseManager

from .managers import (
    UserProfileManager,
)

User = get_user_model()


class UserProfile(BaseAuditData):
    """Holds Users profile data.
    """
    password_status_choice = (
        ('T', 'Temporary'),
        ('S', 'Set'),
    )

    user_profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        related_name='userprofile',
        on_delete=models.CASCADE,
        db_index=True,
    )
    phone = models.CharField(
        max_length=15,
        help_text="Your Phone number",
        null=True,
        blank=True,
    )
    initials = models.CharField(
        max_length=10,
        help_text="Your Initials",
        null=True,
        blank=True,
        default=''
    )
    thumbnail = models.URLField(
        max_length=settings.BIG_CHAR_FIELD_LENGTH,
        help_text="The Thumbnail",
        blank=True,
        null=True,
    )
    password_status = models.CharField(
        max_length=1,
        choices=password_status_choice,
        default='T'
    )

    password_version = models.PositiveIntegerField(default=0)

    objects = UserProfileManager()

    def save(self, *args, **kwargs):
        """
        """
        self.initials = ''
        names = self.name.split(' ')
        for name in names:
            try:
                self.initials += name[0].upper()
            except IndexError:
                continue

        try:
            self.initials = self.initials[:2]
        except:  # noqa E722
            pass

        super().save(*args, **kwargs)

    @cached_property
    def name(self):
        """
        """
        name = "%s %s" % (self.user.first_name, self.user.last_name)
        if not name.strip():
            name = self.user.email if self.user.email else self.user.username
        return name.strip()


class ForgotPasswordRequests(BaseAuditData):
    """
    """
    forgot_password_request_id = models.AutoField(primary_key=True)
    request_id = models.UUIDField(max_length=36, default=uuid4)
    is_satisfied = models.BooleanField(default=False)
    user = models.ForeignKey(
        User,
        related_name='ForgotPasswordRequests',
        on_delete=models.CASCADE,
    )

    objects = BaseManager()

    @property
    def is_expired(self):
        """
        """
        now = datetime.now(tz=pytz.UTC)
        if now > self.valid_till:
            return True
        return False

    @property
    def is_valid(self):
        """
        """
        if not self.is_expired and not self.is_satisfied:
            return True
        return False

    @property
    def valid_till(self):
        delta = timedelta(hours=24)
        return self.time_created + delta

