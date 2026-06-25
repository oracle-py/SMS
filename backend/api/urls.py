"""
URL configuration for API.

This module defines the URL patterns for the API,
including versioned routes.
"""

from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('v1/', include('api.v1.urls')),
]
