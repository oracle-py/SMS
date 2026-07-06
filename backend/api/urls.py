"""
URL configuration for API.

This module defines the URL patterns for the API,
including versioned routes.
"""

from django.urls import path, include
from django.http import JsonResponse
import socket


def test_email(request):
    """
    Network connectivity test to smtp.gmail.com.
    Tests if the machine can reach Gmail SMTP server.
    """
    try:
        socket.create_connection(("smtp.gmail.com", 587), timeout=5)
        return JsonResponse({"success": True, "message": "Connected to Gmail SMTP"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


app_name = 'api'

urlpatterns = [
    path('test-email/', test_email),
    path('v1/', include('api.v1.urls')),
]
