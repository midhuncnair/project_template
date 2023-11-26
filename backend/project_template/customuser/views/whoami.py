"""
The user whoami specific views
"""


# from __future__ import


__all__ = [
    'WhoAmI',
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
from rest_framework.response import (
    Response
)

from project_template.base import (
    BaseListCreateAPIView,
    BaseRetriveUpdateDestroyAPIView,
    BaseAPIView,
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


class WhoAmI(BaseAPIView):
    permission_classes = (
        IsAuthenticated,
        UserBasePermission,
    )
    def get(self, request, *args, **kwargs):
        """
        """
        logger.debug("in WhoAmI get with inp %s, %s", args, kwargs)
        logger.debug("in WhoAmI get with user %s", request.user)

        up_obj = UserProfile.objects.get(user=request.user)
        print("up_obj = ", up_obj)

        return Response(UserProfileSerializer(up_obj).data)
