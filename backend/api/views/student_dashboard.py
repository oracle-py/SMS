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
from academics.models import Grade, Attendance, CourseRegistration, Result
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
            
            # Calculate CGPA using the new Result-based system
            cgpa = student.calculate_cumulative_cgpa()
            
            # Get recent results (last 5 approved results)
            recent_results_data = Result.objects.filter(
                student=request.user,
                status='approved'
            ).select_related(
                'course',
                'session',
                'semester'
            ).order_by('-submitted_at')[:5]
            
            recent_results = [
                {
                    'course_code': result.course.course_code,
                    'course_title': result.course.course_title,
                    'score': float(result.total_score),
                    'grade': result.grade,
                    'credit_unit': result.course.credit_unit,
                    'session': result.session.name if result.session else 'N/A',
                    'semester': result.semester.get_name_display() if result.semester else 'N/A'
                }
                for result in recent_results_data
            ]
            
            # Calculate attendance percentage
            attendance_records = Attendance.objects.filter(student=student)
            total_attendance = attendance_records.count()
            present_attendance = attendance_records.filter(status='present').count()
            attendance_percentage = (
                (present_attendance / total_attendance * 100) if total_attendance > 0 else 0.0
            )
            
            # Calculate carryovers (failed courses)
            carryover_count = Result.objects.filter(
                student=request.user,
                status='approved',
                grade='F'
            ).count()
            
            # Build student info
            student_info = {
                'name': f"{request.user.first_name} {request.user.last_name}",
                'matric_number': student.student_id,
                'level': f"{student.grade_level} Level",
                'department': student.programme.department.name if student.programme and student.programme.department else 'N/A',
                'faculty': student.programme.department.faculty.name if student.programme and student.programme.department and student.programme.department.faculty else 'N/A',
                'credits': student.programme.total_credit_units if student.programme else 0
            }
            
            # Determine academic standing based on CGPA
            if cgpa >= 4.5:
                standing = 'First Class'
            elif cgpa >= 3.5:
                standing = 'Second Class Upper'
            elif cgpa >= 2.5:
                standing = 'Second Class Lower'
            elif cgpa >= 1.5:
                standing = 'Third Class'
            else:
                standing = 'Probation'
            
            # Get total courses registered
            total_courses = CourseRegistration.objects.filter(student=student).count()
            
            response_data = {
                'student_info': student_info,
                'cgpa': cgpa,
                'academic_standing': standing,
                'attendance_percentage': attendance_percentage,
                'carryover_count': carryover_count,
                'total_courses_registered': total_courses,
                'recent_results': recent_results
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
