"""
The url page for customuser module
"""


# from __future__ import


__all__ = []
__version__ = "1.0.0.0"
__author__ = "Midhun C Nair <midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair <midhunch@gmail.com>",
]


from django.urls import path

from .views import (
    UserList,
    UserDetail,
    WhoAmI,
)


urlpatterns = [
    path('', UserList.as_view(), name='users'),
    path('<int:pk>/', UserDetail.as_view(), name='user'),
    path('whoami/', WhoAmI.as_view(), name='whoami'),
]
