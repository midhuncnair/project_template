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


from project_template.base import BaseManager


class UserProfileManager(BaseManager):
    def get_queryset(self, apply_filter=True):
        """
        overrides the default get_queryset
        """
        # queryset = QuerySetManager(self.model, using=self._db)
        self.prefetch_related_args = None
        self.select_related_args = (
            'user',
        )
        self.filter_kwargs = {
            'is_active': True,
        }
        if apply_filter:
            return super().get_queryset().filter(**self.filter_kwargs)

        return super().get_queryset()
