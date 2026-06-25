"""
Student dashboard views.

This module provides business intelligence endpoints for student dashboards,
including academic summaries, results, and attendance information.

Performance optimization: Dashboard endpoints are cached for 5 minutes
to reduce database load and improve response times.
"""

from typing import Dict, Any, List

from django.conf import settings
from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import StudentProfile
from users.permissions import IsStudentRole
from academics.models import Grade, Attendance, CourseRegistration
from academics.services import (
    StudentDashboardService,
    GPAService,
    AcademicStandingService,
    SemesterSummaryService,
)
from api.serializers import (
    StudentDashboardSerializer,
    StudentResultSerializer,
    StudentAttendanceSerializer,
    ErrorResponseSerializer,
)


class StudentDashboardView(GenericAPIView):
    """
    Student dashboard endpoint.
    
    Provides a comprehensive academic summary for the authenticated student
    including CGPA, academic standing, attendance, and recent results.
    """
    
    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = StudentDashboardSerializer
    
    @extend_schema(
        responses={
            200: StudentDashboardSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    
    def get(self, request) -> Response:
        """
        Get student dashboard summary.
        
        Returns:
            Response with comprehensive student dashboard data
        """
        try:
            student = request.user.student_profile
            
            # Generate cache key
            cache_key = f'student_dashboard_{student.id}'
            
            # Try to get cached data
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data, status=status.HTTP_200_OK)
            
            # Get dashboard data from service layer
            dashboard_data = StudentDashboardService.get_student_dashboard(student)
            
            # Get recent results (last 5 grades)
            recent_grades = Grade.objects.filter(
                registration__student=student
            ).select_related(
                'registration__course',
                'registration__session',
                'registration__semester'
            ).order_by('-created_at')[:5]
            
            recent_results = [
                {
                    'course_code': grade.registration.course.course_code,
                    'course_title': grade.registration.course.course_title,
                    'score': float(grade.score),
                    'grade': grade.letter_grade,
                    'session': grade.registration.session.name,
                    'semester': grade.registration.semester.get_name_display()
                }
                for grade in recent_grades
            ]
            
            # Build student info
            student_info = {
                'name': f"{request.user.first_name} {request.user.last_name}",
                'matric_number': student.student_id,
                'level': student.grade_level
            }
            
            response_data = {
                'student_info': student_info,
                'cgpa': dashboard_data['cgpa'],
                'academic_standing': dashboard_data['standing'],
                'attendance_percentage': dashboard_data['attendance_percentage'],
                'carryover_count': dashboard_data['carryover_count'],
                'total_courses_registered': dashboard_data['total_courses'],
                'recent_results': recent_results
            }
            
            # Cache the response for 5 minutes
            cache.set(cache_key, response_data, getattr(settings, 'DASHBOARD_CACHE_TIMEOUT', 300))
            
            return Response(
                {'success': True, 'data': response_data},
                status=status.HTTP_200_OK
            )
            
        except StudentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Student profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentResultsView(GenericAPIView):
    """
    Student results endpoint.
    
    Returns all grades for the authenticated student with optional filtering
    by session, semester, or course.
    """
    
    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = StudentResultSerializer
    
    @extend_schema(
        responses={
            200: StudentResultSerializer(many=True),
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    
    def get(self, request) -> Response:
        """
        Get student results with optional filtering.
        
        Query parameters:
            - session: Filter by session ID
            - semester: Filter by semester ID
            - course: Filter by course ID
            
        Returns:
            Response with student results data
        """
        try:
            student = request.user.student_profile
            
            # Build queryset with filters
            queryset = Grade.objects.filter(
                registration__student=student
            ).select_related(
                'registration__course',
                'registration__session',
                'registration__semester'
            ).order_by('-created_at')
            
            # Apply filters
            session_id = request.query_params.get('session')
            semester_id = request.query_params.get('semester')
            course_id = request.query_params.get('course')
            
            if session_id:
                queryset = queryset.filter(registration__session_id=session_id)
            if semester_id:
                queryset = queryset.filter(registration__semester_id=semester_id)
            if course_id:
                queryset = queryset.filter(registration__course_id=course_id)
            
            # Build response data
            results = [
                {
                    'course_code': grade.registration.course.course_code,
                    'course_title': grade.registration.course.course_title,
                    'score': float(grade.score),
                    'letter_grade': grade.letter_grade,
                    'grade_point': grade.grade_point,
                    'session': grade.registration.session.name,
                    'semester': grade.registration.semester.get_name_display(),
                    'credit_unit': grade.registration.course.credit_unit
                }
                for grade in queryset
            ]
            
            return Response(
                {'success': True, 'data': results},
                status=status.HTTP_200_OK
            )
            
        except StudentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Student profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentAttendanceView(GenericAPIView):
    """
    Student attendance endpoint.
    
    Returns attendance records for the authenticated student with optional
    filtering by course, session, or semester.
    """
    
    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = StudentAttendanceSerializer
    
    @extend_schema(
        responses={
            200: StudentAttendanceSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    
    def get(self, request) -> Response:
        """
        Get student attendance with optional filtering.
        
        Query parameters:
            - course: Filter by course ID
            - session: Filter by session ID
            - semester: Filter by semester ID
            
        Returns:
            Response with student attendance data
        """
        try:
            student = request.user.student_profile
            
            # Build queryset with filters
            queryset = Attendance.objects.filter(
                student=student
            ).select_related('course').order_by('-date')
            
            # Apply filters
            course_id = request.query_params.get('course')
            session_id = request.query_params.get('session')
            semester_id = request.query_params.get('semester')
            
            if course_id:
                queryset = queryset.filter(course_id=course_id)
            if session_id:
                queryset = queryset.filter(course__semester__session_id=session_id)
            if semester_id:
                queryset = queryset.filter(course__semester_id=semester_id)
            
            # Calculate attendance percentage
            total_records = queryset.count()
            present_records = queryset.filter(status='present').count()
            attendance_percentage = (
                (present_records / total_records * 100) if total_records > 0 else 0.0
            )
            
            # Build attendance records
            records = [
                {
                    'course': attendance.course.course_code,
                    'course_title': attendance.course.course_title,
                    'date': attendance.date.isoformat(),
                    'status': attendance.status,
                    'remarks': attendance.remarks
                }
                for attendance in queryset
            ]
            
            response_data = {
                'attendance_percentage': round(attendance_percentage, 2),
                'total_records': total_records,
                'present_records': present_records,
                'absent_records': total_records - present_records,
                'records': records
            }
            
            return Response(
                {'success': True, 'data': response_data},
                status=status.HTTP_200_OK
            )
            
        except StudentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Student profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
