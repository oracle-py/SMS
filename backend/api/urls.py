"""
URL configuration for API.

This module defines the URL patterns for the API,
including versioned routes.
"""

from django.urls import path, include
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings


def test_email(request):
    """
    Standalone email test endpoint to isolate SMTP configuration issues.
    """
    try:
        send_mail(
            subject="SMTP Test",
            message="This is a test email.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["conectuj@gmail.com"],  # Replace with your test email
            fail_silently=False,
        )
        return JsonResponse({"success": True, "message": "Email sent successfully"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


app_name = 'api'

urlpatterns = [
    path('test-email/', test_email),
    path('v1/', include('api.v1.urls')),
]
