#! /usr/bin/env python
"""Base Models
"""


__all__ = [
    "BaseQuerySetManager",
    "BaseManager",
    "BaseAuditData",
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import logging


from django.db import models, router
from django.utils import timezone

from .collector import Collector

logger = logging.getLogger(__name__)


class BaseQuerySetManager(models.query.QuerySet):
    """Overrides the django's default queryset
    to include custom logics for soft delete and purge
    """
    def _soft_delete(self, request_id):
        """does a soft delete
        """
        if request_id is None:
            from project_template.request_utils.context import get_current_context
            try:
                request_id = get_current_context()
            except:
                pass

        """Delete the records in the current QuerySet."""
        self._not_support_combined_queries('delete')
        assert not self.query.is_sliced, \
            "Cannot use 'limit' or 'offset' with delete."

        if self.query.distinct or self.query.distinct_fields:
            raise TypeError('Cannot call delete() after .distinct().')
        if self._fields is not None:
            raise TypeError("Cannot call delete() after .values() or .values_list()")

        del_query = self._chain()

        # The delete is actually 2 queries - one to find related objects,
        # and one to delete. Make sure that the discovery of related
        # objects is performed on the same database as the deletion.
        del_query._for_write = True

        # Disable non-supported fields.
        del_query.query.select_for_update = False
        del_query.query.select_related = False
        del_query.query.clear_ordering(force_empty=True)

        collector = Collector(using=del_query.db)
        collector.collect(del_query)
        deleted, _rows_count = collector.soft_delete(request_id)

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None
        return deleted, _rows_count

    def delete(self, is_soft=True, request_id=None):
        """overrides the default delete to be soft
        """
        if is_soft is False:
            super().delete()
        else:
            self._soft_delete(request_id)

    delete.alters_data = True
    delete.queryset_only = True

    def undelete(self, request_id=None):
        """
        undo soft delete.
        """
        if request_id is None:
            from project_template.request_utils.context import get_current_context
            try:
                request_id = get_current_context()
            except:
                pass

        """Delete the records in the current QuerySet."""
        self._not_support_combined_queries('delete')
        assert not self.query.is_sliced, \
            "Cannot use 'limit' or 'offset' with delete."

        if self.query.distinct or self.query.distinct_fields:
            raise TypeError('Cannot call delete() after .distinct().')
        if self._fields is not None:
            raise TypeError("Cannot call delete() after .values() or .values_list()")

        del_query = self._chain()

        # The delete is actually 2 queries - one to find related objects,
        # and one to delete. Make sure that the discovery of related
        # objects is performed on the same database as the deletion.
        del_query._for_write = True

        # Disable non-supported fields.
        del_query.query.select_for_update = False
        del_query.query.select_related = False
        del_query.query.clear_ordering(force_empty=True)

        collector = Collector(using=del_query.db)
        collector.collect(del_query)
        deleted, _rows_count = collector.undo_soft_delete(request_id)

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None
        return deleted, _rows_count

    undelete.alters_data = True
    undelete.queryset_only = True

    def update(self, *args, **kwargs):
        """
        """
        ret_data = super().update(*args, **kwargs)
        return ret_data

    def __include_deleted(self, kwargs):
        include_deleted = kwargs.get('__include_deleted')
        if '__include_deleted' in kwargs:
            del kwargs['__include_deleted']

        return bool(include_deleted), kwargs

    def get(self, *args, **kwargs):
        """
        """
        logger.debug("The get of base queryset called with args %s and kwargs %s", args, kwargs)

        include_deleted, kwargs = self.__include_deleted(kwargs)
        if include_deleted is False:
            kwargs['is_active'] = True

        return super().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        """
        """
        logger.debug("The filter of base queryset called with args %s and kwargs %s", args, kwargs)

        include_deleted, kwargs = self.__include_deleted(kwargs)
        if include_deleted is False:
            kwargs['is_active'] = True

        return super().filter(*args, **kwargs)


class BaseManager(models.Manager):
    """Manager for models with additional logic to accomodate soft delete
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)

        self.filter_kwargs = None
        self.prefetch_related_args = None
        self.select_related_args = None
        self.QuerySetManager = BaseQuerySetManager


    def __include_deleted(self, kwargs):
        include_deleted = kwargs.get('__include_deleted')
        if '__include_deleted' in kwargs:
            del kwargs['__include_deleted']

        return bool(include_deleted), kwargs

    def get_queryset(self):
        """
        overrides the default get_queryset
        """
        # logger.debug("the self.select_related_args = %s", self.select_related_args)
        # logger.debug("the self.prefetch_related_args = %s", self.prefetch_related_args)
        queryset = self.QuerySetManager(self.model, using=self._db)
        if self.select_related_args is not None:
            queryset = queryset.select_related(*self.select_related_args)
        if self.prefetch_related_args is not None:
            queryset = queryset.prefetch_related(*self.prefetch_related_args)

        return queryset

    def create(self, *args, **kwargs):
        """
        """
        ret_data = super().create(*args, **kwargs)
        return ret_data

    def update(self, *args, **kwargs):
        """
        """
        ret_data = super().update(*args, **kwargs)
        return ret_data

    def get(self, *args, **kwargs):
        """
        """
        logger.debug("The get of base Manager called with args %s and kwargs %s", args, kwargs)

        include_deleted, kwargs = self.__include_deleted(kwargs)
        if include_deleted is False:
            kwargs['is_active'] = True

        return super().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        """
        """
        logger.debug("The filter of base Manager called with args %s and kwargs %s", args, kwargs)

        include_deleted, kwargs = self.__include_deleted(kwargs)
        if include_deleted is False:
            kwargs['is_active'] = True

        return super().filter(*args, **kwargs)


class BaseAuditData(models.Model):
    """
    This class defines the audit fields
    """
    time_created = models.DateTimeField(
        # auto_now_add=True,
        # editable=False
        default=timezone.now
    )
    time_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(default='', blank=True)
    requests = models.ManyToManyField('appmanagement.RequestTracker')
    objects = models.Manager()  # default
    raw_objects = models.Manager()

    def _soft_delete(self, request_id):
        """Performs a soft delete on the object and related objects
        """
        if request_id is None:
            from project_template.request_utils.context import get_current_context
            try:
                request_id = get_current_context()
            except:
                pass

        using = router.db_for_write(self._meta.model, instance=self)
        assert self._get_pk_val()is not None, \
            "%s object can't be deleted because its %s attribute is set to None." % (
                self._meta.object_name,
                self._meta.pk.attname
            )

        collector = Collector(using=using)
        collector.collect([self])
        collector.soft_delete(request_id)

    def delete(self, is_soft=True, request_id=None):
        """
        overrides the model delete to set only
        is_active = False
        """
        if is_soft:
            self._soft_delete(request_id)
        else:
            super().delete()

    def undelete(self, request_id=None):
        """Undoes the soft delete
        """
        if request_id is None:
            from project_template.request_utils.context import get_current_context
            try:
                request_id = get_current_context()
            except:
                pass

        using = router.db_for_write(self._meta.model, instance=self)
        assert self._get_pk_val()is not None, \
            "%s object can't be undeleted because its %s attribute is set to None." % (
                self._meta.object_name,
                self._meta.pk.attname
            )

        collector = Collector(using=using)
        collector.collect([self])
        collector.undo_soft_delete(request_id)

    def save(self, *args, **kwargs):
        request_id = kwargs.get('request_id')
        if request_id is None:
            from project_template.request_utils.context import get_current_context
            try:
                request_id = get_current_context()
            except:
                pass
        else:
            del kwargs['request_id']

        remarks = '' if self.remarks is None else self.remarks + '\n'
        created_updated = 'Created' if self.pk is None else 'Updated'
        self.remarks = f"{remarks}RequestId:{request_id} --> {created_updated}"

        if self.time_created is None:
            self.time_created = timezone.now()

        ret_data = super().save(*args, **kwargs)
        self.refresh_from_db()
        self.requests.add(request_id)
        return ret_data

    class Meta:
        abstract = True
