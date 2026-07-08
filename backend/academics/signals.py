"""
Signals for automatic course assignment.

This module provides Django signals to automatically assign new courses
to existing students when courses are created or updated.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import logging

from academics.models import Course, CourseRegistration, AcademicSession
from users.models import StudentProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Course)
def assign_course_to_existing_students(sender, instance, created, **kwargs):
    """
    Automatically assign a newly created course to all existing students in the same level.
    
    When a course is created or updated, this signal assigns it to all students
    whose grade_level matches the course's level.
    
    Args:
        sender: The Course model class
        instance: The Course instance that was saved
        created: Boolean indicating if this was a new instance
        **kwargs: Additional keyword arguments
    """
    # Only process if the course is active and has a level
    if not instance.is_active or not instance.level:
        logger.info(f"Skipping course assignment for {instance.course_code} - inactive or no level")
        return
    
    logger.info(f"Processing course: {instance.course_code} (level: {instance.level.name})")
    
    try:
        # Get current academic session
        current_session = AcademicSession.objects.filter(is_active=True).first()
        if not current_session:
            logger.warning("No current academic session found, using first available session")
            current_session = AcademicSession.objects.first()
        
        if not current_session:
            logger.error("No academic session available for course assignment")
            return
        
        logger.info(f"Using session: {current_session.name}")
        
        # Get the level number from the level name (e.g., "100 Level" -> 100)
        level_name = instance.level.name
        try:
            grade_level = int(level_name.split()[0])
        except (ValueError, IndexError):
            logger.error(f"Could not parse grade level from level name: {level_name}")
            return
        
        logger.info(f"Grade level: {grade_level}")
        
        # Get all students in this grade level
        students = StudentProfile.objects.filter(grade_level=grade_level)
        logger.info(f"Found {students.count()} students in level {grade_level}")
        
        if students.count() == 0:
            logger.info(f"No students found in level {grade_level}")
            return
        
        # Assign course to each student
        assigned_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for student in students:
                # Check if already registered
                existing = CourseRegistration.objects.filter(
                    student=student,
                    course=instance,
                    session=current_session,
                    semester=instance.semester
                ).exists()
                
                if not existing:
                    CourseRegistration.objects.create(
                        student=student,
                        course=instance,
                        session=current_session,
                        semester=instance.semester,
                        is_carryover=False
                    )
                    assigned_count += 1
                    logger.info(f"Assigned {instance.course_code} to student {student.student_id}")
                else:
                    skipped_count += 1
                    logger.info(f"Student {student.student_id} already registered for {instance.course_code}")
        
        logger.info(f"Course assignment complete: {assigned_count} assigned, {skipped_count} skipped")
        
    except Exception as e:
        logger.error(f"Error assigning course to existing students: {e}", exc_info=True)
