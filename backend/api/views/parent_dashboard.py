"""
Parent dashboard views.

This module provides business intelligence endpoints for parent dashboards,
including monitoring of linked students' academic performance.

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

from users.models import ParentProfile, ParentStudentRelation, StudentProfile
from users.permissions import IsParentRole
from academics.models import Grade, Attendance
from academics.services import (
    StudentDashboardService,
    GPAService,
    AcademicStandingService,
)
from api.serializers import (
    ParentDashboardSerializer,
    ParentWardSerializer,
    ErrorResponseSerializer,
)


class ParentDashboardView(GenericAPIView):
    """
    Parent dashboard endpoint.
    
    Provides an overview of all students linked to the authenticated parent,
    including their CGPA, academic standing, and attendance.
    """
    
    permission_classes = [IsAuthenticated, IsParentRole]
    serializer_class = ParentDashboardSerializer
    
    @extend_schema(
        responses={
            200: ParentDashboardSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    
    def get(self, request) -> Response:
        """
        Get parent dashboard summary with all linked students.
        
        Returns:
            Response with comprehensive parent dashboard data
        """
        try:
            parent = request.user.parent_profile
            
            # Generate cache key
            cache_key = f'parent_dashboard_{parent.id}'
            
            # Try to get cached data
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data, status=status.HTTP_200_OK)
            
            # Get all students linked to this parent
            relations = ParentStudentRelation.objects.filter(
                parent=parent
            ).select_related('student__user', 'student')
            
            wards_data = []
            
            for relation in relations:
                student = relation.student
                
                # Get dashboard data for each student using service layer
                dashboard_data = StudentDashboardService.get_student_dashboard(student)
                
                ward_info = {
                    'student_id': student.id,
                    'name': f"{student.user.first_name} {student.user.last_name}",
                    'matric_number': student.student_id,
                    'level': student.grade_level,
                    'cgpa': dashboard_data['cgpa'],
                    'academic_standing': dashboard_data['standing'],
                    'attendance_percentage': dashboard_data['attendance_percentage'],
                    'carryover_count': dashboard_data['carryover_count'],
                    'total_courses': dashboard_data['total_courses'],
                    'relationship_type': relation.relationship_type
                }
                
                wards_data.append(ward_info)
            
            response_data = {
                'parent_name': f"{request.user.first_name} {request.user.last_name}",
                'total_wards': len(wards_data),
                'wards': wards_data
            }
            
            # Cache the response for 5 minutes
            cache.set(cache_key, response_data, getattr(settings, 'DASHBOARD_CACHE_TIMEOUT', 300))
            
            return Response(
                {'success': True, 'data': response_data},
                status=status.HTTP_200_OK
            )
            
        except ParentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Parent profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ParentWardDetailView(GenericAPIView):
    """
    Parent ward detail endpoint.
    
    Provides detailed academic information for a specific linked student.
    Parents can only access students they are linked to.
    """
    
    permission_classes = [IsAuthenticated, IsParentRole]
    serializer_class = ParentWardSerializer
    
    @extend_schema(
        responses={
            200: ParentWardSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    
    def get(self, request, student_id: int) -> Response:
        """
        Get detailed academic summary for a specific linked student.
        
        Args:
            student_id: ID of the student to retrieve details for
            
        Returns:
            Response with detailed student academic data
        """
        try:
            parent = request.user.parent_profile
            
            # Verify parent is linked to this student
            relation = ParentStudentRelation.objects.filter(
                parent=parent,
                student_id=student_id
            ).first()
            
            if not relation:
                return Response(
                    {'success': False, 'error': 'You are not authorized to view this student\'s information.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            student = relation.student
            
            # Generate cache key
            cache_key = f'parent_ward_detail_{parent.id}_{student_id}'
            
            # Try to get cached data
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data, status=status.HTTP_200_OK)
            
            # Get comprehensive dashboard data using service layer
            dashboard_data = StudentDashboardService.get_student_dashboard(student)
            
            # Get recent results (last 10 grades)
            recent_grades = Grade.objects.filter(
                registration__student=student
            ).select_related(
                'registration__course',
                'registration__session',
                'registration__semester'
            ).order_by('-created_at')[:10]
            
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
                for grade in recent_grades
            ]
            
            # Get carryover courses
            carryovers = GPAService.get_carryover_courses(student)
            carryover_data = [
                {
                    'course_code': carry.registration.course.course_code,
                    'course_title': carry.registration.course.course_title,
                    'score': float(carry.score),
                    'letter_grade': carry.letter_grade,
                    'session': carry.registration.session.name,
                    'semester': carry.registration.semester.get_name_display()
                }
                for carry in carryovers
            ]
            
            # Get attendance records (last 20)
            attendance_records = Attendance.objects.filter(
                student=student
            ).select_related('course').order_by('-date')[:20]
            
            attendance_data = [
                {
                    'course': attendance.course.course_code,
                    'course_title': attendance.course.course_title,
                    'date': attendance.date.isoformat(),
                    'status': attendance.status,
                    'remarks': attendance.remarks
                }
                for attendance in attendance_records
            ]
            
            # Build student info
            student_info = {
                'student_id': student.id,
                'name': f"{student.user.first_name} {student.user.last_name}",
                'matric_number': student.student_id,
                'level': student.grade_level,
                'email': student.user.email
            }
            
            response_data = {
                'student_info': student_info,
                'cgpa': dashboard_data['cgpa'],
                'academic_standing': dashboard_data['standing'],
                'attendance_percentage': dashboard_data['attendance_percentage'],
                'carryover_count': dashboard_data['carryover_count'],
                'total_courses': dashboard_data['total_courses'],
                'relationship_type': relation.relationship_type,
                'results': results,
                'carryovers': carryover_data,
                'attendance_records': attendance_data
            }
            
            # Cache the response for 5 minutes
            cache.set(cache_key, response_data, getattr(settings, 'DASHBOARD_CACHE_TIMEOUT', 300))
            
            return Response(
                {'success': True, 'data': response_data},
                status=status.HTTP_200_OK
            )
            
        except ParentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Parent profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except StudentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Student not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
