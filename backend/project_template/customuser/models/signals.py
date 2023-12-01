#! /usr/bin/env python
"""Signals for customuser app
"""


__all__ = [
    'create_user_profile',
    'lowercase_user_username',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import logging


from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import UserProfile


logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(
    post_save,
    sender=User,
    dispatch_uid="User:create_user_profile"
)
def create_user_profile(sender, instance, created=False, **kwargs):
    if created:
        if not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)
    else:
        try:
            instance.userprofile.save()
        except Exception as err:
            if (err.__class__.__name__.find('RelatedObjectDoesNotExist') != -1):
                print("Related object doesn't exist")
            logging.critical(
                "An Error occured while saving rhe user profile and is %s:%s",
                err.__class__.__name__,
                str(err),
            )
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.save()


@receiver(
    post_save,
    sender=User,
    dispatch_uid="User:lowercase_user_username"
)
def lowercase_user_username(sender, instance, created=False, **kwargs):
    changed = False
    if not instance.username.islower():
        instance.username = instance.username.lower()
        changed = True

    if not instance.email.islower():
        instance.email = instance.email.lower()
        changed = True

    if changed:
        instance.save()
