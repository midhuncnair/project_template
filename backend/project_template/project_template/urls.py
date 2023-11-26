"""
URL configuration for project_template project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from project_template.jwt_utils import (
    AppTokenObtainPairView,
    AppTokenObtainSlidingView,
)
from customuser import urls as cu_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/', TokenObtainSlidingView.as_view(), name='token_obtain_sliding'),
    path('api/token/', AppTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/slidingtoken/', AppTokenObtainSlidingView.as_view(), name='token_obtain_sliding'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/<str:version>/users/', include(cu_urls)),
]