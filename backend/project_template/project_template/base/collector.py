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

    def query_update_batch(self, model, pk_list, update_data):
        """
        """
        query = sql.UpdateQuery(model)
        return query.update_batch(
            pk_list,
            update_data,
            self.using
        )

    def compute_requests_through_model_n_data(self, model_obj, pk_list, request_id):
        """
        """
        RequestsThroughModel = None
        through_bulk_create = []
        if hasattr(model_obj, 'requests'):
            RequestsThroughModel = model_obj.requests.through
            through_bulk_create = [
                RequestsThroughModel(pk, request_id=request_id)
                for pk in pk_list
            ]

        return RequestsThroughModel, through_bulk_create

    def soft_delete(self, request_id):
        """soft delete the records and also add the user who deleted it.
        """

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
                        remarks = '' if instance.remarks is None else instance.remarks + '\n'
                        remarks += f"RequestId:{request_id} --> SoftDelete"
                        count = self.query_update_batch(
                            model,
                            pk_list=[instance.pk],
                            update_data={
                                'is_active': False,
                                'remarks': remarks
                            }
                        )
                        if hasattr(instance, 'requests'):
                            instance.requests.add(request_id)
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
                                remarks = '' if instance.remarks is None else instance.remarks + '\n'
                                remarks += f"RequestId:{request_id} --> SoftDelete"
                                instance.is_active = False
                                instance.remarks = remarks
                                instance.save()
                                deleted_counter[qs.model._meta.label] += 1
                        except FieldDoesNotExist:
                            pass

            # delete instances
            for model, instances in self.data.items():
                try:
                    model._meta.get_field('is_active')  # will throw error if field doesn't exist.
                    pk_list = [obj.pk for obj in instances if obj.is_active is True]

                    count = self.query_update_batch(
                        model,
                        pk_list=pk_list,
                        update_data={
                            'is_active': False,
                            'remarks': Concat(
                                'remarks',
                                V(f'\nRequestId:{request_id} --> SoftDelete'),
                                output_field=TextField()
                            )
                        }
                    )
                    RequestsThroughModel, through_bulk_create = (
                        self.compute_requests_through_model_n_data(
                            instances[0],
                            pk_list=pk_list,
                            request_id=request_id
                        )
                    )
                    if (
                            RequestsThroughModel is not None
                            and len(through_bulk_create) > 0  # this should be true if count>0
                        ):
                            RequestsThroughModel.objects.bulk_create(through_bulk_create)

                    if count:
                        deleted_counter[model._meta.label] += count

                except FieldDoesNotExist:
                    pass

        return sum(deleted_counter.values()), dict(deleted_counter)

    def undo_soft_delete(self, request_id):
        """undoes the soft delete of the records and also add the user who undeleted it.
        """
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
                        remarks = '' if instance.remarks is None else instance.remarks + '\n'
                        remarks += f"RequestId:{request_id} --> UndoSoftDelete"
                        count = self.query_update_batch(
                            model,
                            pk_list=[instance.pk],
                            update_data={
                                'is_active': True,
                                'remarks': remarks,
                            }
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
                                remarks = '' if instance.remarks is None else instance.remarks + '\n'
                                remarks += f"RequestId:{request_id} --> UndoSoftDelete"
                                instance.is_active = True
                                instance.remarks = remarks
                                instance.save()
                                deleted_counter[qs.model._meta.label] += 1
                        except FieldDoesNotExist:
                            pass

            # delete instances
            for model, instances in self.data.items():
                try:
                    model._meta.get_field('is_active')  # will throw error if field doesn't exist.
                    pk_list = [obj.pk for obj in instances if obj.is_active is False]
                    count = self.query_update_batch(
                        model,
                        pk_list=pk_list,
                        update_data={
                            'is_active': True,
                            'remarks': Concat(
                                'remarks',
                                V(f'\nRequestId:{request_id} --> UndoSoftDelete'),
                                output_field=TextField()
                            )
                        }
                    )
                    RequestsThroughModel, through_bulk_create = (
                        self.compute_requests_through_model_n_data(
                            instances[0],
                            pk_list=pk_list,
                            request_id=request_id
                        )
                    )
                    if (
                            RequestsThroughModel is not None
                            and len(through_bulk_create) > 0  # this should be true if count>0
                        ):
                            RequestsThroughModel.objects.bulk_create(through_bulk_create)

                    if count:
                        deleted_counter[model._meta.label] += count

                except FieldDoesNotExist:
                    pass

        return sum(deleted_counter.values()), dict(deleted_counter)
