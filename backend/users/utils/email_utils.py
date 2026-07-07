from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime
import logging
import requests

logger = logging.getLogger(__name__)


def send_registration_email(user_type, recipient_email, context):
    """
    Send registration email to students, lecturers, or parents using Brevo API.
    
    Args:
        user_type (str): Type of user ('student', 'lecturer', 'parent')
        recipient_email (str): Email address of the recipient
        context (dict): Context data for the email template
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        logger.info(f"Attempting to send {user_type} registration email to {recipient_email}")
        
        # Add common context
        context['year'] = datetime.now().year
        context['login_url'] = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000/login')
        
        # Select template based on user type
        template_map = {
            'student': 'emails/student_registration.html',
            'lecturer': 'emails/lecturer_registration.html',
            'parent': 'emails/parent_registration.html'
        }
        
        template_name = template_map.get(user_type)
        if not template_name:
            raise ValueError(f"Invalid user type: {user_type}")
        
        # Render HTML content
        html_content = render_to_string(template_name, context)
        
        # Create email subject
        subject_map = {
            'student': 'Welcome to School Monitoring System - Your Student Account',
            'lecturer': 'Welcome to School Monitoring System - Your Lecturer Account',
            'parent': 'Welcome to School Monitoring System - Your Parent Account'
        }
        
        subject = subject_map.get(user_type, 'Welcome to School Monitoring System')
        
        # Generate plain text content from HTML (basic fallback)
        text_content = html_content.replace('<br>', '\n').replace('<br/>', '\n')
        import re
        text_content = re.sub('<[^<]+?>', '', text_content)
        
        # Send email using Brevo API
        logger.info("=== USING BREVO HTTP API ===")

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json",
            },
            json={
                "sender": {
                    "name": "PLASU",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                "to": [
                    {
                        "email": recipient_email,
                    }
                ],
                "subject": subject,
                "htmlContent": html_content,
                "textContent": text_content,
            },
            timeout=15,
        )
        
        logger.info(f"Brevo Status: {response.status_code}")
        logger.info(f"Brevo Response: {response.text}")

        response.raise_for_status()

        return True
        
    except Exception as e:
        logger.error(f"Error sending registration email to {recipient_email}: {str(e)}", exc_info=True)
        return False


def send_student_registration_email(email, first_name, last_name, matric_number, password, school_email=None):
    """Send registration email to a student."""
    context = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'matric_number': matric_number,
        'password': password,
        'school_email': school_email or email  # Fallback to email if school_email not provided
    }
    return send_registration_email('student', email, context)


def send_lecturer_registration_email(email, first_name, last_name, staff_id, department, rank, password, school_email=None):
    """Send registration email to a lecturer."""
    context = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'staff_id': staff_id,
        'department': department,
        'rank': rank,
        'password': password,
        'school_email': school_email or email  # Fallback to email if school_email not provided
    }
    return send_registration_email('lecturer', email, context)


def send_parent_registration_email(email, first_name, last_name, password, child_name=None, child_matric=None, school_email=None):
    """Send registration email to a parent."""
    context = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'child_name': child_name,
        'child_matric': child_matric,
        'school_email': school_email or email  # Fallback to email if school_email not provided
    }
    return send_registration_email('parent', email, context)
