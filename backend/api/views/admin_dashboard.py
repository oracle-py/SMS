"""
Admin dashboard views.

This module provides business intelligence endpoints for admin dashboards,
including statistics, recent registrations, pending results, and activity logs.
"""

from typing import Dict, Any, List

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User, StudentProfile, ParentProfile, LecturerProfile
from users.permissions import IsAdminRole
from academics.models import Course, Grade, CourseRegistration, ActivityLog, Department, Faculty
from api.serializers import ErrorResponseSerializer


class AdminDashboardView(GenericAPIView):
    """
    Admin dashboard endpoint.
    
    Provides comprehensive statistics and overview data for administrators.
    """
    
    permission_classes = [IsAuthenticated, IsAdminRole]
    
    @extend_schema(
        responses={
            200: dict,
            403: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    
    def get(self, request) -> Response:
        """
        Get admin dashboard statistics and overview data.
        
        Returns:
            Response with comprehensive admin dashboard data
        """
        try:
            # Calculate statistics
            total_students = StudentProfile.objects.count()
            total_lecturers = LecturerProfile.objects.count()
            total_parents = ParentProfile.objects.count()
            total_courses = Course.objects.filter(is_active=True).count()
            total_faculties = Faculty.objects.count()
            
            # Calculate weekly changes (last 7 days)
            from django.utils import timezone
            from datetime import timedelta
            week_ago = timezone.now() - timedelta(days=7)
            
            students_this_week = StudentProfile.objects.filter(enrollment_date__gte=week_ago).count()
            lecturers_this_week = LecturerProfile.objects.filter(user__date_joined__gte=week_ago).count()
            parents_this_week = ParentProfile.objects.filter(user__date_joined__gte=week_ago).count()
            # Courses don't have created_at, so we'll just show 0 for now
            courses_this_week = 0
            
            # Get recent registrations (last 5 students)
            recent_students = StudentProfile.objects.select_related(
                'user', 'programme', 'programme__department'
            ).order_by('-enrollment_date', '-id')[:5]
            
            recent_registrations = []
            for student in recent_students:
                recent_registrations.append({
                    'name': f"{student.user.first_name} {student.user.last_name}",
                    'student_id': student.student_id,
                    'department': student.programme.department.name if student.programme else 'N/A',
                    'level': f"{student.grade_level} Level",
                    'enrollment_date': student.enrollment_date.isoformat()
                })
            
            # Get pending results (Result model with pending status)
            from academics.models import Result
            pending_results_data = Result.objects.filter(status='pending').select_related(
                'course', 'lecturer', 'session', 'semester'
            ).order_by('-submitted_at')[:5]
            
            pending_results = []
            for result in pending_results_data:
                # Format: "CS101 submitted for review"
                course_code = result.course.course_code
                lecturer_name = f"{result.lecturer.first_name} {result.lecturer.last_name}" if result.lecturer else 'Unknown'
                
                # Count students registered for this course
                student_count = CourseRegistration.objects.filter(
                    course=result.course,
                    session=result.session,
                    semester=result.semester
                ).count()
                
                pending_results.append({
                    'course_code': course_code,
                    'course_title': result.course.course_title,
                    'lecturer': lecturer_name,
                    'session': result.session.name,
                    'semester': result.semester.get_name_display(),
                    'submitted_at': result.submitted_at.isoformat() if result.submitted_at else None,
                    'display_message': f"{course_code} submitted for review",
                    'students': student_count
                })
            
            # Get recent activity logs (last 10)
            recent_activities = ActivityLog.objects.select_related(
                'user'
            ).order_by('-created_at')[:10]
            
            activities = []
            for activity in recent_activities:
                activities.append({
                    'user': activity.user.username if activity.user else 'System',
                    'action': activity.action,
                    'entity_type': activity.entity_type,
                    'description': activity.description,
                    'timestamp': activity.created_at.isoformat()
                })
            
            # Build response data
            response_data = {
                'statistics': {
                    'students': {
                        'total': total_students,
                        'change_this_week': f"+{students_this_week}" if students_this_week > 0 else "0"
                    },
                    'lecturers': {
                        'total': total_lecturers,
                        'change_this_week': f"+{lecturers_this_week}" if lecturers_this_week > 0 else "0"
                    },
                    'parents': {
                        'total': total_parents,
                        'change_this_week': f"+{parents_this_week}" if parents_this_week > 0 else "0"
                    },
                    'courses': {
                        'total': total_courses,
                        'change_this_week': f"+{courses_this_week}" if courses_this_week > 0 else "0"
                    },
                    'faculties': {
                        'total': total_faculties
                    }
                },
                'recent_registrations': recent_registrations,
                'pending_results': pending_results,
                'recent_activities': activities,
                'pending_results_count': Result.objects.filter(status='pending').count()
            }
            
            return Response(
                {'success': True, 'data': response_data},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'success': False, 'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
