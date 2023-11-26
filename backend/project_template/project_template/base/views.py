#! /usr/bin/env python3
"""This module contains common view utility functions
"""


# from __future__ import


__all__ = [
    'BaseAPIView',
    'BaseListCreateAPIView',
    'BaseRetriveUpdateDestroyAPIView',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


from rest_framework.views import APIView
from rest_framework import generics


class BaseAPIView(APIView):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)


class BaseListCreateAPIView(generics.ListCreateAPIView):
    """
    """
    def get_queryset(self):
        """
        """
        qs = super().get_queryset()
        print("BaseListCreateAPIView: self.args, self.kwargs = ", self.args, self.kwargs)
        return qs


class BaseRetriveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    def get_queryset(self):
        """
        """
        qs = super().get_queryset()
        print("BaseRetriveUpdateDestroyAPIView: self.args, self.kwargs = ", self.args, self.kwargs)
        return qs
