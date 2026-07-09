"""
Views for course assignment operations.

This module provides API endpoints for manual course assignment,
including individual student assignment, level-based assignment, and bulk operations.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
import logging

from academics.utils import log_activity


def get_client_ip(request):
    """
    Get the client IP address from the request.
    
    Args:
        request: The HTTP request object
        
    Returns:
        The client IP address or None
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from academics.models import Course, CourseRegistration, AcademicSession, Level
from users.models import StudentProfile
from users.permissions import IsAdminRole

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def assign_course_to_student(request):
    """
    Assign a specific course to a specific student.
    
    Request body:
    {
        "student_id": str (matric number),
        "course_id": int,
        "lecturer_id": int (required),
        "session_id": int (optional)
    }
    """
    try:
        student_id = request.data.get('student_id')
        course_id = request.data.get('course_id')
        lecturer_id = request.data.get('lecturer_id')
        session_id = request.data.get('session_id')

        if not student_id or not course_id:
            return Response(
                {'success': False, 'error': 'student_id and course_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not lecturer_id:
            return Response(
                {'success': False, 'error': 'lecturer_id is required - courses must be assigned to a lecturer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get student by matric number
        student = StudentProfile.objects.get(student_id=student_id)
        
        # Get course
        course = Course.objects.get(id=course_id)
        
        # Get session
        if session_id:
            session = AcademicSession.objects.get(id=session_id)
        else:
            session = AcademicSession.objects.filter(is_active=True).first()
            if not session:
                session = AcademicSession.objects.first()
        
        if not session:
            return Response(
                {'success': False, 'error': 'No academic session available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already registered
        existing = CourseRegistration.objects.filter(
            student=student,
            course=course,
            session=session,
            semester=course.semester
        ).exists()

        if existing:
            return Response(
                {'success': False, 'error': 'Student already registered for this course'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create course assignment (required)
        from academics.models import CourseAssignment
        from users.models import User
        
        try:
            lecturer = User.objects.get(id=lecturer_id, role='lecturer')
            
            # Check if assignment already exists
            assignment_exists = CourseAssignment.objects.filter(
                course=course,
                lecturer=lecturer,
                session=session,
                semester=course.semester
            ).exists()
            
            if not assignment_exists:
                CourseAssignment.objects.create(
                    course=course,
                    lecturer=lecturer,
                    session=session,
                    semester=course.semester,
                    role='primary'
                )
        except User.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Lecturer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create registration
        CourseRegistration.objects.create(
            student=student,
            course=course,
            session=session,
            semester=course.semester,
            is_carryover=False
        )

        return Response({
            'success': True,
            'message': f'Successfully assigned course {course.course_code} to {student.student_id}'
        })

    except StudentProfile.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Course.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Course not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error assigning course to student: {e}", exc_info=True)
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def assign_level_courses_to_student(request):
    """
    Assign all courses for a level to a specific student.
    
    Request body:
    {
        "student_id": str (matric number),
        "grade_level": int (optional, will use student's grade_level if not provided),
        "lecturer_id": int (optional - will assign all courses to this lecturer)
    }
    """
    try:
        student_id = request.data.get('student_id')
        grade_level = request.data.get('grade_level')
        lecturer_id = request.data.get('lecturer_id')

        if not student_id:
            return Response(
                {'success': False, 'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get student by matric number
        student = StudentProfile.objects.get(student_id=student_id)
        
        # Use provided grade_level or student's grade_level
        target_grade_level = grade_level if grade_level else student.grade_level
        
        # Find level object
        level_name_variants = [
            f"{target_grade_level} Level",
            str(target_grade_level),
            f"{target_grade_level}L",
            f"L{target_grade_level}"
        ]
        
        level = None
        for level_name in level_name_variants:
            level = Level.objects.filter(name__iexact=level_name).first()
            if level:
                break
        
        if not level:
            level = Level.objects.filter(name__icontains=str(target_grade_level)).first()
        
        if not level:
            return Response(
                {'success': False, 'error': f'Level for grade {target_grade_level} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get lecturer if provided
        lecturer = None
        if lecturer_id:
            from users.models import User
            try:
                lecturer = User.objects.get(id=lecturer_id, role='lecturer')
            except User.DoesNotExist:
                return Response(
                    {'success': False, 'error': 'Lecturer not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Get current session
        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            session = AcademicSession.objects.first()
        
        if not session:
            return Response(
                {'success': False, 'error': 'No academic session available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get courses for this level
        courses = Course.objects.filter(level=level, is_active=True)
        if courses.count() == 0:
            courses = Course.objects.filter(level=level)
        
        if courses.count() == 0:
            return Response(
                {'success': False, 'error': f'No courses found for level {level.name}'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Assign courses
        assigned_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for course in courses:
                existing = CourseRegistration.objects.filter(
                    student=student,
                    course=course,
                    session=session,
                    semester=course.semester
                ).exists()
                
                if not existing:
                    CourseRegistration.objects.create(
                        student=student,
                        course=course,
                        session=session,
                        semester=course.semester,
                        is_carryover=False
                    )
                    assigned_count += 1
                else:
                    skipped_count += 1
                
                # Create course assignment if lecturer is provided
                if lecturer:
                    from academics.models import CourseAssignment
                    assignment_exists = CourseAssignment.objects.filter(
                        course=course,
                        lecturer=lecturer,
                        session=session,
                        semester=course.semester
                    ).exists()
                    
                    if not assignment_exists:
                        CourseAssignment.objects.create(
                            course=course,
                            lecturer=lecturer,
                            session=session,
                            semester=course.semester,
                            role='primary'
                        )

        course_word = 'course' if assigned_count == 1 else 'courses'
        registered_word = 'course' if skipped_count == 1 else 'courses'
        # Log activity
        try:
            log_activity(
                user=request.user,
                action='ASSIGN_COURSES',
                entity_type='Student',
                entity_id=student.id,
                description=f"Assigned {assigned_count} {course_word} to student {student.student_id}",
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)
        
        return Response({
            'success': True,
            'message': f'Successfully assigned {assigned_count} {course_word} to {student.student_id}. {skipped_count} {registered_word} now registered.'
        })

    except StudentProfile.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error assigning level courses to student: {e}", exc_info=True)
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def assign_courses_to_level_students(request):
    """
    Assign all courses for a level to all students in that level.
    
    Request body:
    {
        "grade_level": int
    }
    """
    try:
        grade_level = request.data.get('grade_level')

        if not grade_level:
            return Response(
                {'success': False, 'error': 'grade_level is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find level object
        level_name_variants = [
            f"{grade_level} Level",
            str(grade_level),
            f"{grade_level}L",
            f"L{grade_level}"
        ]
        
        level = None
        for level_name in level_name_variants:
            level = Level.objects.filter(name__iexact=level_name).first()
            if level:
                break
        
        if not level:
            level = Level.objects.filter(name__icontains=str(grade_level)).first()
        
        if not level:
            return Response(
                {'success': False, 'error': f'Level for grade {grade_level} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get students in this grade level
        students = StudentProfile.objects.filter(grade_level=grade_level)
        
        if students.count() == 0:
            return Response(
                {'success': False, 'error': f'No students found in level {grade_level}'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get current session
        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            session = AcademicSession.objects.first()
        
        if not session:
            return Response(
                {'success': False, 'error': 'No academic session available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get courses for this level
        courses = Course.objects.filter(level=level, is_active=True)
        if courses.count() == 0:
            courses = Course.objects.filter(level=level)
        
        if courses.count() == 0:
            return Response(
                {'success': False, 'error': f'No courses found for level {level.name}'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Assign courses to all students
        total_assigned = 0
        total_skipped = 0
        
        with transaction.atomic():
            for student in students:
                for course in courses:
                    existing = CourseRegistration.objects.filter(
                        student=student,
                        course=course,
                        session=session,
                        semester=course.semester
                    ).exists()
                    
                    if not existing:
                        CourseRegistration.objects.create(
                            student=student,
                            course=course,
                            session=session,
                            semester=course.semester,
                            is_carryover=False
                        )
                        total_assigned += 1
                    else:
                        total_skipped += 1

        assigned_word = 'course' if total_assigned == 1 else 'courses'
        registered_word = 'course' if total_skipped == 1 else 'courses'
        student_word = 'student' if students.count() == 1 else 'students'
        
        # Log activity
        try:
            log_activity(
                user=request.user,
                action='ASSIGN_COURSES_LEVEL',
                entity_type='Level',
                entity_id=level.id,
                description=f"Assigned {total_assigned} {assigned_word} to {students.count()} {student_word} in {level.name}",
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)
        
        return Response({
            'success': True,
            'message': f'Successfully assigned {total_assigned} {assigned_word} to {students.count()} {student_word}. {total_skipped} {registered_word} now registered.'
        })

    except Exception as e:
        logger.error(f"Error assigning courses to level students: {e}", exc_info=True)
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def assign_courses_to_all_students(request):
    """
    Assign courses to all students based on their grade levels.
    This is a one-button solution to assign all courses to all students.
    """
    try:
        # Get current session
        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            session = AcademicSession.objects.first()
        
        if not session:
            return Response(
                {'success': False, 'error': 'No academic session available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get all levels
        levels = Level.objects.all()
        
        total_assigned = 0
        total_skipped = 0
        level_summary = []

        for level in levels:
            # Parse grade level
            level_name = level.name
            try:
                grade_level = int(level_name.split()[0])
            except (ValueError, IndexError):
                continue

            # Get students in this grade level
            students = StudentProfile.objects.filter(grade_level=grade_level)
            
            if students.count() == 0:
                continue

            # Get courses for this level
            courses = Course.objects.filter(level=level, is_active=True)
            if courses.count() == 0:
                courses = Course.objects.filter(level=level)
            
            if courses.count() == 0:
                continue

            # Assign courses
            level_assigned = 0
            level_skipped = 0
            
            with transaction.atomic():
                for student in students:
                    for course in courses:
                        existing = CourseRegistration.objects.filter(
                            student=student,
                            course=course,
                            session=session,
                            semester=course.semester
                        ).exists()
                        
                        if not existing:
                            CourseRegistration.objects.create(
                                student=student,
                                course=course,
                                session=session,
                                semester=course.semester,
                                is_carryover=False
                            )
                            level_assigned += 1
                        else:
                            level_skipped += 1

            total_assigned += level_assigned
            total_skipped += level_skipped
            level_summary.append({
                'level': level.name,
                'students': students.count(),
                'assigned': level_assigned,
                'skipped': level_skipped
            })

        assigned_word = 'course' if total_assigned == 1 else 'courses'
        registered_word = 'course' if total_skipped == 1 else 'courses'
        
        # Log activity
        try:
            log_activity(
                user=request.user,
                action='ASSIGN_COURSES_ALL',
                entity_type='System',
                entity_id=0,
                description=f"Assigned {total_assigned} {assigned_word} to all students",
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)
        
        return Response({
            'success': True,
            'message': f'Successfully assigned {total_assigned} {assigned_word} to all students. {total_skipped} {registered_word} now registered.',
            'summary': level_summary
        })

    except Exception as e:
        logger.error(f"Error assigning courses to all students: {e}", exc_info=True)
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
