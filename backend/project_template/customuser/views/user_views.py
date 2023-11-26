"""
The user specific views
"""


# from __future__ import


__all__ = [
    'UserList',
    'UserDetail',
]
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]

import logging

from rest_framework.permissions import (
    IsAuthenticated,
)
# from rest_framework.parsers import (
#     JSONParser,
#     MultiPartParser,
#     FormParser,
# )

from project_template.base import (
    BaseListCreateAPIView,
    BaseRetriveUpdateDestroyAPIView,
)

from customuser.permissions import (
    UserBasePermission,
)
from customuser.models import (
    UserProfile,
)
from customuser.serializers import (
    UserProfileSerializer,
)


logger = logging.getLogger(__name__)


class UserList(BaseListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (
        IsAuthenticated,
        UserBasePermission,
    )
    # parser_classes = (
    #     JSONParser,
    #     FormParser,
    #     MultiPartParser,
    # )


class UserDetail(BaseRetriveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (
        IsAuthenticated,
        UserBasePermission,
    )
