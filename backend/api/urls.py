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
    Network connectivity test comparing google.com vs smtp.gmail.com.
    Tests if the machine can reach general internet vs SMTP specifically.
    """
    results = {}
    
    # Test general internet connectivity
    try:
        socket.create_connection(("google.com", 443), timeout=5)
        results["google_com"] = {"success": True, "message": "Connected to google.com:443"}
    except Exception as e:
        results["google_com"] = {"success": False, "error": str(e)}
    
    # Test SMTP connectivity
    try:
        socket.create_connection(("smtp.gmail.com", 587), timeout=5)
        results["smtp_gmail"] = {"success": True, "message": "Connected to smtp.gmail.com:587"}
    except Exception as e:
        results["smtp_gmail"] = {"success": False, "error": str(e)}
    
    return JsonResponse(results)


app_name = 'api'

urlpatterns = [
    path('test-email/', test_email),
    path('v1/', include('api.v1.urls')),
]
