"""
URL configuration for notification_service project.

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
from rest_framework.routers import DefaultRouter

from notification_app.views import ClientViewSet, MailingViewSet, index, api_documentation

router = DefaultRouter()
router.register('clients', ClientViewSet, basename='clients')
router.register('mailings', MailingViewSet, basename='mailings')

urlpatterns = [
    path('', index, name='index'),
    path('docs/', api_documentation, name='api_docs'),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
]
