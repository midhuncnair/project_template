#! /usr/bin/env python
"""serialisers for simple jwt extention
"""


__all__ = [
    'AppTokenObtainPairSerializer',
    'AppTokenObtainSlidingSerializer',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import logging

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSlidingSerializer,
)


logger = logging.getLogger(__name__)


class AppTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.username
        return token

    @property
    def validated_data(self):
        ret_data = super().validated_data
        # Add addtional data in the token if you need here
        # look at the class definition of TokenObtainPairSerializer to see what
        # all contextual data is there like self.user
        return ret_data


class AppTokenObtainSlidingSerializer(TokenObtainSlidingSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.username
        return token

    @property
    def validated_data(self):
        ret_data = super().validated_data
        # Add addtional data in the token if you need here
        # look at the class definition of TokenObtainPairSerializer to see what
        # all contextual data is there like self.user
        return ret_data
