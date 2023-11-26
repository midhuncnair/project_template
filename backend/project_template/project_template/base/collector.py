#! /usr/bin/env python
"""Custom extensions
"""


__all__ = [
    'Collector',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]



import logging


from collections import Counter
from operator import attrgetter

from django.db import transaction
from django.db.models import sql, Value as V, TextField
from django.db.models.functions import Concat
from django.db.models.deletion import Collector as BaseCollector
from django.core.exceptions import FieldDoesNotExist


logger = logging.getLogger(__name__)


class Collector(BaseCollector):
    """This helps us to delete the related table records
    """

    def get_user_api_path(self, request):
        """Constructs the user and apiPath fromthe request if exists.
        """
        user = request.user.username if (request and request.user) else ''
        apiPath = (
            request.get_full_path() + '::' + request.method.upper()
            if request else '<path>::<method>'
        )
        return user, apiPath

    def soft_delete(self, request=None):
        """soft delete the records and also add the user who deleted it.
        """
        user, apiPath = self.get_user_api_path(request)

        for model, instances in self.data.items():
            self.data[model] = sorted(instances, key=attrgetter("pk"))

        # if possible, bring the models in an order suitable for databases that
        # don't support transactions or cannot defer constraint checks until the
        # end of a transaction.
        self.sort()
        # number of objects deleted for each model label
        deleted_counter = Counter()

        # Optimize for the case with a single obj and no dependencies
        if len(self.data) == 1 and len(instances) == 1:
            instance = list(instances)[0]
            if self.can_fast_delete(instance):
                if hasattr(instance, 'is_active') and instance.is_active == True:
                    with transaction.mark_for_rollback_on_error(self.using):
                        count = sql.UpdateQuery(model).update_batch(
                            [instance.pk],
                            {
                                'is_active': False,
                                'remarks': instance.remarks + '\n' + "Deleted by " + str(user) + "As Part of '" + apiPath + "'"
                            },
                            self.using
                        )
                    # setattr(instance, model._meta.pk.attname, None)
                    return count, {model._meta.label: count}
                else:
                    return 0, {model._meta.label: 0}

        with transaction.atomic(using=self.using, savepoint=False):
            # fast deletes
            if hasattr(self, 'fast_deletes'):
                for qs in self.fast_deletes:
                    for instance in qs:
                        try:
                            if hasattr(instance, 'is_active') and instance.is_active == True:
                                instance.is_active = False
                                instance.remarks += '\n' + "Deleted by " + str(user) + "As Part of '" + apiPath + "'"
                                instance.save()
                                deleted_counter[qs.model._meta.label] += 1
                        except FieldDoesNotExist:
                            pass

            # delete instances
            for model, instances in self.data.items():
                try:
                    model._meta.get_field('is_active')  # will throw error if field doesn't exist.
                    query = sql.UpdateQuery(model)
                    pk_list = [obj.pk for obj in instances if obj.is_active is True]
                    count = query.update_batch(
                        pk_list,
                        {
                            'is_active': False,
                            'remarks': Concat(
                                'remarks',
                                V('\nDeleted by ' + str(user) + "As Part of '" + apiPath + "'"),
                                output_field=TextField()
                            )
                        },
                        self.using
                    )
                    if count:
                        deleted_counter[model._meta.label] += count

                except FieldDoesNotExist:
                    pass

        return sum(deleted_counter.values()), dict(deleted_counter)

    def undo_soft_delete(self, request=None):
        """undoes the soft delete of the records and also add the user who undeleted it.
        """
        user, apiPath = self.get_user_api_path(request)
        # sort instance collections
        for model, instances in self.data.items():
            self.data[model] = sorted(instances, key=attrgetter("pk"))

        # if possible, bring the models in an order suitable for databases that
        # don't support transactions or cannot defer constraint checks until the
        # end of a transaction.
        self.sort()
        # number of objects deleted for each model label
        deleted_counter = Counter()

        # Optimize for the case with a single obj and no dependencies
        if len(self.data) == 1 and len(instances) == 1:
            instance = list(instances)[0]
            if self.can_fast_delete(instance):
                if hasattr(instance, 'is_active') and instance.is_active == False:
                    with transaction.mark_for_rollback_on_error(self.using):
                        count = sql.UpdateQuery(model).update_batch(
                            [instance.pk],
                            {
                                'is_active': True,
                                'remarks': instance.remarks + '\n' + "UnDeleted by " + str(user) + "As Part of '" + apiPath + "'"
                            },
                            self.using
                        )
                    # setattr(instance, model._meta.pk.attname, None)
                    return count, {model._meta.label: count}
                else:
                    return 0, {model._meta.label: 0}

        with transaction.atomic(using=self.using, savepoint=False):
            # fast deletes
            if hasattr(self, 'fast_deletes'):
                for qs in self.fast_deletes:
                    for instance in qs:
                        try:
                            if hasattr(instance, 'is_active') and instance.is_active == False:
                                instance.is_active = True
                                instance.save()
                                instance.remarks += '\n' + "UnDeleted by " + str(user) + "As Part of '" + apiPath + "'"
                                deleted_counter[qs.model._meta.label] += 1
                        except FieldDoesNotExist:
                            pass

            # delete instances
            for model, instances in self.data.items():
                try:
                    model._meta.get_field('is_active')  # will throw error if field doesn't exist.
                    query = sql.UpdateQuery(model)
                    pk_list = [obj.pk for obj in instances if obj.is_active is False]
                    count = query.update_batch(
                        pk_list,
                        {
                            'is_active': True,
                            'remarks': Concat(
                                'remarks',
                                V('\nUnDeleted by ' + str(user) + "As Part of '" + apiPath + "'"),
                                output_field=TextField()
                            )
                        },
                        self.using
                    )
                    if count:
                        deleted_counter[model._meta.label] += count

                except FieldDoesNotExist:
                    pass

        return sum(deleted_counter.values()), dict(deleted_counter)
