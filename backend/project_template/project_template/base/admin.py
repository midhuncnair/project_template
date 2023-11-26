#! /usr/bin/env python
"""admin base
"""


__all__ = [
    "BaseModelAdmin",
    "BaseAdminFilterMixin",
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]



import logging

from django.contrib import admin

from .collector import Collector


logger = logging.getLogger(__name__)


class BaseModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = self.model.raw_objects.get_queryset()

        # we need this from the superclass method
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def undo_soft_delete(self, request, queryset):
        """
        """
        collector = Collector(using=queryset.db)
        collector.collect(queryset.filter(is_active=False))
        collector.undo_soft_delete(request)

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None

    def soft_delete(self, request, queryset):
        pks = queryset.values_list('pk', flat=True)
        n_queryset = self.model.objects.filter(pk__in=pks)
        n_queryset.delete(request)

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None

    actions = admin.ModelAdmin.actions + ('undo_soft_delete', 'soft_delete')
    undo_soft_delete.short_description = 'Undo Soft Delete'
    soft_delete.short_description = 'Soft Delete'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        related_model = db_field.related_model
        objects = (
            related_model.raw_objects
            if hasattr(related_model, 'raw_objects')
            else related_model.objects
        )
        logger.debug("The Related Model in formfield_for_foreignkey = %s, %s", related_model, objects)
        kwargs["queryset"] = objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        related_model = db_field.related_model
        objects = (
            related_model.raw_objects
            if hasattr(related_model, 'raw_objects')
            else related_model.objects
        )
        logger.debug("The Related Model in formfield_for_manytomany = %s, %s", related_model, objects)
        kwargs["queryset"] = objects.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class BaseAdminFilterMixin(admin.SimpleListFilter):
    """
    """
    def get_query(self):
        query = dict()
        return query

    def get_query_parameter(self):
        """
        """
        return 'pk'

    def get_transformed_value(self):
        """
        """
        return self.value()

    def queryset(self, request, queryset):
        """
        """
        query = self.get_query()
        query_parameter = self.get_query_parameter()
        value = self.get_transformed_value()

        if value is not None:
            query[query_parameter] = value
        if query:
            return queryset.filter(**query)
        else:
            return queryset
