#! /usr/bin/env python
"""views for simple jwt extention
"""


__all__ = [
    'AppTokenObtainPairView',
    'AppTokenObtainSlidingView',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import logging

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenObtainSlidingView,
)

from .serializers import (
    AppTokenObtainPairSerializer,
    AppTokenObtainSlidingSerializer,
)


logger = logging.getLogger(__name__)


class AppTokenObtainPairView(TokenObtainPairView):
    serializer_class = AppTokenObtainPairSerializer

class AppTokenObtainSlidingView(TokenObtainSlidingView):
    serializer_class = AppTokenObtainSlidingSerializer
