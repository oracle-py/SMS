"""
Utility functions for academics module.

This module provides helper functions for activity logging and other common operations.
"""

import logging
from django.utils import timezone
from academics.models import ActivityLog

logger = logging.getLogger(__name__)


def log_activity(user, action, entity_type, entity_id, description, ip_address=None):
    """
    Log an activity to the ActivityLog model.
    
    Args:
        user: The user who performed the action
        action: The action performed (e.g., 'CREATE_STUDENT', 'APPROVE_RESULT')
        entity_type: The type of entity affected (e.g., 'Student', 'Course')
        entity_id: The ID of the entity affected
        description: Human-readable description of the action
        ip_address: Optional IP address of the user
    """
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address
        )
        logger.info(f"Activity logged: {action} on {entity_type} {entity_id} by {user.username if user else 'System'}")
    except Exception as e:
        logger.error(f"Failed to log activity: {e}", exc_info=True)
