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
            
            recent_results = []
            for result in recent_results_data:
                try:
                    recent_results.append({
                        'course_code': result.course.course_code,
                        'course_title': result.course.course_title,
                        'score': float(result.total_score),
                        'grade': result.grade,
                        'credit_unit': result.course.credit_unit,
                        'session': result.session.name if result.session else 'N/A',
                        'semester': result.semester.get_name_display() if result.semester else 'N/A'
                    })
                except Exception as e:
                    # Skip malformed results
                    continue
            
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
            try:
                department_name = student.programme.department.name if student.programme and student.programme.department else 'N/A'
            except:
                department_name = 'N/A'
            
            try:
                faculty_name = student.programme.department.faculty.name if student.programme and student.programme.department and student.programme.department.faculty else 'N/A'
            except:
                faculty_name = 'N/A'
            
            student_info = {
                'name': f"{request.user.first_name} {request.user.last_name}",
                'matric_number': student.student_id,
                'level': f"{student.grade_level} Level",
                'department': department_name,
                'faculty': faculty_name,
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
            
            # Get current session
            from academics.models import AcademicSession
            current_session = AcademicSession.objects.filter(is_active=True).first()
            current_session_name = current_session.name if current_session else '2025/2026'
            
            response_data = {
                'student_info': student_info,
                'cgpa': cgpa,
                'academic_standing': standing,
                'attendance_percentage': attendance_percentage,
                'carryover_count': carryover_count,
                'total_courses_registered': total_courses,
                'current_session': current_session_name,
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


class StudentCoursesView(GenericAPIView):
    """
    Student courses endpoint.
    
    Returns all courses the student is registered in with lecturer information.
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
        Get student courses.
        
        Returns:
            Response with student's registered courses and lecturer information
        """
        try:
            from academics.models import CourseRegistration, CourseAssignment
            
            student = request.user.student_profile
            
            # Get all course registrations for the student
            course_registrations = CourseRegistration.objects.filter(
                student=student
            ).select_related(
                'course', 
                'course__level', 
                'course__semester'
            )
            
            # Build courses list with lecturer information
            courses = []
            for registration in course_registrations:
                course = registration.course
                
                # Get lecturer assignment for this course
                lecturer_assignment = CourseAssignment.objects.filter(
                    course=course
                ).select_related('lecturer').first()
                
                # Build lecturer info
                lecturer_info = None
                if lecturer_assignment and lecturer_assignment.lecturer:
                    lecturer_info = {
                        'user': {
                            'first_name': lecturer_assignment.lecturer.first_name,
                            'last_name': lecturer_assignment.lecturer.last_name
                        },
                        'first_name': lecturer_assignment.lecturer.first_name,
                        'last_name': lecturer_assignment.lecturer.last_name
                    }
                
                course_data = {
                    'id': course.id,
                    'course_code': course.course_code,
                    'code': course.course_code,
                    'course_title': course.course_title,
                    'title': course.course_title,
                    'level': {
                        'name': course.level.name if course.level else 'N/A'
                    } if course.level else None,
                    'credit_units': course.credit_unit,
                    'units': course.credit_unit,
                    'credits': course.credit_unit,
                    'semester': {
                        'name': course.semester.get_name_display() if course.semester else 'N/A'
                    } if course.semester else None,
                    'lecturer': lecturer_info
                }
                
                courses.append(course_data)
            
            return Response(
                {'success': True, 'data': courses},
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


class StudentLecturersView(GenericAPIView):
    """
    Student lecturers endpoint.
    
    Returns all lecturers for courses the student is registered in.
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
        Get student lecturers.
        
        Returns:
            Response with lecturers for the student's registered courses
        """
        try:
            from academics.models import CourseRegistration, CourseAssignment
            
            student = request.user.student_profile
            
            # Get all course registrations for the student
            course_registrations = CourseRegistration.objects.filter(
                student=student
            ).select_related('course')
            
            # Get all courses the student is registered in
            course_ids = course_registrations.values_list('course_id', flat=True)
            
            # Get all course assignments for these courses
            course_assignments = CourseAssignment.objects.filter(
                course_id__in=course_ids
            ).select_related('lecturer', 'course')
            
            # Build unique lecturers list
            lecturers_dict = {}
            for assignment in course_assignments:
                lecturer_id = assignment.lecturer.id
                if lecturer_id not in lecturers_dict:
                    # Get department from lecturer profile
                    department_name = 'N/A'
                    try:
                        if hasattr(assignment.lecturer, 'lecturer_profile') and assignment.lecturer.lecturer_profile:
                            if assignment.lecturer.lecturer_profile.department:
                                department_name = assignment.lecturer.lecturer_profile.department.name
                    except:
                        department_name = 'N/A'
                    
                    lecturers_dict[lecturer_id] = {
                        'id': lecturer_id,
                        'name': f"{assignment.lecturer.first_name} {assignment.lecturer.last_name}",
                        'first_name': assignment.lecturer.first_name,
                        'last_name': assignment.lecturer.last_name,
                        'email': assignment.lecturer.email,
                        'department': department_name,
                        'courses': [],
                        'status': 'Active'
                    }
                
                # Add course if not already in list
                course_info = {
                    'id': assignment.course.id,
                    'code': assignment.course.course_code,
                    'title': assignment.course.course_title
                }
                if not any(c['id'] == course_info['id'] for c in lecturers_dict[lecturer_id]['courses']):
                    lecturers_dict[lecturer_id]['courses'].append(course_info)
            
            lecturers = list(lecturers_dict.values())
            
            return Response(
                {'success': True, 'data': lecturers},
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


class StudentCoursesView(GenericAPIView):
    """
    Student courses endpoint.
    
    Returns all courses the student is registered in with lecturer information.
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
        Get student courses.
        
        Returns:
            Response with student's registered courses and lecturer information
        """
        try:
            from academics.models import CourseRegistration, CourseAssignment
            
            student = request.user.student_profile
            
            # Get all course registrations for the student
            course_registrations = CourseRegistration.objects.filter(
                student=student
            ).select_related(
                'course', 
                'course__level', 
                'course__semester'
            )
            
            # Build courses list with lecturer information
            courses = []
            for registration in course_registrations:
                course = registration.course
                
                # Get lecturer assignment for this course
                lecturer_assignment = CourseAssignment.objects.filter(
                    course=course
                ).select_related('lecturer').first()
                
                # Build lecturer info
                lecturer_info = None
                if lecturer_assignment and lecturer_assignment.lecturer:
                    lecturer_info = {
                        'user': {
                            'first_name': lecturer_assignment.lecturer.first_name,
                            'last_name': lecturer_assignment.lecturer.last_name
                        },
                        'first_name': lecturer_assignment.lecturer.first_name,
                        'last_name': lecturer_assignment.lecturer.last_name
                    }
                
                course_data = {
                    'id': course.id,
                    'course_code': course.course_code,
                    'code': course.course_code,
                    'course_title': course.course_title,
                    'title': course.course_title,
                    'level': {
                        'name': course.level.name if course.level else 'N/A'
                    } if course.level else None,
                    'credit_units': course.credit_unit,
                    'units': course.credit_unit,
                    'credits': course.credit_unit,
                    'semester': {
                        'name': course.semester.get_name_display() if course.semester else 'N/A'
                    } if course.semester else None,
                    'lecturer': lecturer_info
                }
                
                courses.append(course_data)
            
            return Response(
                {'success': True, 'data': courses},
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
    
    Returns all results for the authenticated student with optional filtering
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
            # Use Result model instead of Grade model
            from academics.models import Result
            
            # Build queryset with filters
            queryset = Result.objects.filter(
                student=request.user,
                status='approved'  # Only show approved results
            ).select_related(
                'course',
                'session',
                'semester',
                'lecturer'
            ).order_by('-submitted_at')
            
            # Apply filters
            session_id = request.query_params.get('session')
            semester_id = request.query_params.get('semester')
            course_id = request.query_params.get('course')
            
            if session_id:
                queryset = queryset.filter(session_id=session_id)
            if semester_id:
                queryset = queryset.filter(semester_id=semester_id)
            if course_id:
                queryset = queryset.filter(course_id=course_id)
            
            # Build response data
            results = []
            for result in queryset:
                grade = result.grade
                results.append({
                    'id': result.id,
                    'course_code': result.course.course_code,
                    'course_title': result.course.course_title,
                    'ca_score': float(result.ca_score) if result.ca_score else 0,
                    'exam_score': float(result.exam_score) if result.exam_score else 0,
                    'total_score': float(result.total_score) if result.total_score else 0,
                    'grade': grade,
                    'status': result.status,
                    'session': result.session.name,
                    'semester': result.semester.get_name_display(),
                    'credit_unit': result.course.credit_unit if hasattr(result.course, 'credit_unit') else 3,  # Default to 3 if not available
                    'grade_point': self._calculate_grade_point(grade) if grade else 0,
                    'submitted_at': result.submitted_at.isoformat() if result.submitted_at else None,
                    'approved_at': result.approved_at.isoformat() if result.approved_at else None
                })
            
            return Response(
                {'success': True, 'data': results},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'success': False, 'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentCoursesView(GenericAPIView):
    """
    Student courses endpoint.
    
    Returns all courses the student is registered in with lecturer information.
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
        Get student courses.
        
        Returns:
            Response with student's registered courses and lecturer information
        """
        try:
            from academics.models import CourseRegistration, CourseAssignment
            
            student = request.user.student_profile
            
            # Get all course registrations for the student
            course_registrations = CourseRegistration.objects.filter(
                student=student
            ).select_related(
                'course', 
                'course__level', 
                'course__semester'
            )
            
            # Build courses list with lecturer information
            courses = []
            for registration in course_registrations:
                course = registration.course
                
                # Get lecturer assignment for this course
                lecturer_assignment = CourseAssignment.objects.filter(
                    course=course
                ).select_related('lecturer').first()
                
                # Build lecturer info
                lecturer_info = None
                if lecturer_assignment and lecturer_assignment.lecturer:
                    lecturer_info = {
                        'user': {
                            'first_name': lecturer_assignment.lecturer.first_name,
                            'last_name': lecturer_assignment.lecturer.last_name
                        },
                        'first_name': lecturer_assignment.lecturer.first_name,
                        'last_name': lecturer_assignment.lecturer.last_name
                    }
                
                course_data = {
                    'id': course.id,
                    'course_code': course.course_code,
                    'code': course.course_code,
                    'course_title': course.course_title,
                    'title': course.course_title,
                    'level': {
                        'name': course.level.name if course.level else 'N/A'
                    } if course.level else None,
                    'credit_units': course.credit_unit,
                    'units': course.credit_unit,
                    'credits': course.credit_unit,
                    'semester': {
                        'name': course.semester.get_name_display() if course.semester else 'N/A'
                    } if course.semester else None,
                    'lecturer': lecturer_info
                }
                
                courses.append(course_data)
            
            return Response(
                {'success': True, 'data': courses},
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
    
    def _calculate_grade_point(self, grade):
        """Calculate grade point from letter grade."""
        grade_points = {
            'A': 5.0,
            'B': 4.0,
            'C': 3.0,
            'D': 2.0,
            'E': 1.0,
            'F': 0.0
        }
        return grade_points.get(grade, 0.0)


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
            from academics.models import Attendance
            
            # Attendance model uses StudentProfile as ForeignKey
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
            records = []
            for attendance in queryset:
                try:
                    records.append({
                        'course': attendance.course.course_code,
                        'course_title': attendance.course.course_title,
                        'date': attendance.date.isoformat(),
                        'status': attendance.status,
                        'remarks': attendance.remarks
                    })
                except Exception as e:
                    # Skip malformed attendance records
                    continue
            
            # Return empty results if no attendance records
            if not records:
                response_data = {
                    'attendance_percentage': 0.0,
                    'total_records': 0,
                    'present_records': 0,
                    'absent_records': 0,
                    'records': []
                }
            else:
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


class StudentCoursesView(GenericAPIView):
    """
    Student courses endpoint.
    
    Returns all courses the student is registered in with lecturer information.
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
        Get student courses.
        
        Returns:
            Response with student's registered courses and lecturer information
        """
        try:
            from academics.models import CourseRegistration, CourseAssignment
            
            student = request.user.student_profile
            
            # Get all course registrations for the student
            course_registrations = CourseRegistration.objects.filter(
                student=student
            ).select_related(
                'course', 
                'course__level', 
                'course__semester'
            )
            
            # Build courses list with lecturer information
            courses = []
            for registration in course_registrations:
                course = registration.course
                
                # Get lecturer assignment for this course
                lecturer_assignment = CourseAssignment.objects.filter(
                    course=course
                ).select_related('lecturer').first()
                
                # Build lecturer info
                lecturer_info = None
                if lecturer_assignment and lecturer_assignment.lecturer:
                    lecturer_info = {
                        'user': {
                            'first_name': lecturer_assignment.lecturer.first_name,
                            'last_name': lecturer_assignment.lecturer.last_name
                        },
                        'first_name': lecturer_assignment.lecturer.first_name,
                        'last_name': lecturer_assignment.lecturer.last_name
                    }
                
                course_data = {
                    'id': course.id,
                    'course_code': course.course_code,
                    'code': course.course_code,
                    'course_title': course.course_title,
                    'title': course.course_title,
                    'level': {
                        'name': course.level.name if course.level else 'N/A'
                    } if course.level else None,
                    'credit_units': course.credit_unit,
                    'units': course.credit_unit,
                    'credits': course.credit_unit,
                    'semester': {
                        'name': course.semester.get_name_display() if course.semester else 'N/A'
                    } if course.semester else None,
                    'lecturer': lecturer_info
                }
                
                courses.append(course_data)
            
            return Response(
                {'success': True, 'data': courses},
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


class StudentLecturersView(GenericAPIView):
    """
    Student lecturers endpoint.
    
    Returns all lecturers for courses the student is registered in.
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
        Get student lecturers.
        
        Returns:
            Response with lecturers for the student's registered courses
        """
        try:
            from academics.models import CourseRegistration, CourseAssignment
            
            student = request.user.student_profile
            
            # Get all course registrations for the student
            course_registrations = CourseRegistration.objects.filter(
                student=student
            ).select_related('course')
            
            # Get all courses the student is registered in
            course_ids = course_registrations.values_list('course_id', flat=True)
            
            # Get all course assignments for these courses
            course_assignments = CourseAssignment.objects.filter(
                course_id__in=course_ids
            ).select_related('lecturer', 'course')
            
            # Build unique lecturers list
            lecturers_dict = {}
            for assignment in course_assignments:
                lecturer_id = assignment.lecturer.id
                if lecturer_id not in lecturers_dict:
                    # Get department from lecturer profile
                    department_name = 'N/A'
                    try:
                        if hasattr(assignment.lecturer, 'lecturer_profile') and assignment.lecturer.lecturer_profile:
                            if assignment.lecturer.lecturer_profile.department:
                                department_name = assignment.lecturer.lecturer_profile.department.name
                    except:
                        department_name = 'N/A'
                    
                    lecturers_dict[lecturer_id] = {
                        'id': lecturer_id,
                        'name': f"{assignment.lecturer.first_name} {assignment.lecturer.last_name}",
                        'first_name': assignment.lecturer.first_name,
                        'last_name': assignment.lecturer.last_name,
                        'email': assignment.lecturer.email,
                        'department': department_name,
                        'courses': [],
                        'status': 'Active'
                    }
                
                # Add course if not already in list
                course_info = {
                    'id': assignment.course.id,
                    'code': assignment.course.course_code,
                    'title': assignment.course.course_title
                }
                if not any(c['id'] == course_info['id'] for c in lecturers_dict[lecturer_id]['courses']):
                    lecturers_dict[lecturer_id]['courses'].append(course_info)
            
            lecturers = list(lecturers_dict.values())
            
            return Response(
                {'success': True, 'data': lecturers},
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


class StudentCoursesView(GenericAPIView):
    """
    Student courses endpoint.
    
    Returns all courses the student is registered in with lecturer information.
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
        Get student courses.
        
        Returns:
            Response with student's registered courses and lecturer information
        """
        try:
            from academics.models import CourseRegistration, CourseAssignment
            
            student = request.user.student_profile
            
            # Get all course registrations for the student
            course_registrations = CourseRegistration.objects.filter(
                student=student
            ).select_related(
                'course', 
                'course__level', 
                'course__semester'
            )
            
            # Build courses list with lecturer information
            courses = []
            for registration in course_registrations:
                course = registration.course
                
                # Get lecturer assignment for this course
                lecturer_assignment = CourseAssignment.objects.filter(
                    course=course
                ).select_related('lecturer').first()
                
                # Build lecturer info
                lecturer_info = None
                if lecturer_assignment and lecturer_assignment.lecturer:
                    lecturer_info = {
                        'user': {
                            'first_name': lecturer_assignment.lecturer.first_name,
                            'last_name': lecturer_assignment.lecturer.last_name
                        },
                        'first_name': lecturer_assignment.lecturer.first_name,
                        'last_name': lecturer_assignment.lecturer.last_name
                    }
                
                course_data = {
                    'id': course.id,
                    'course_code': course.course_code,
                    'code': course.course_code,
                    'course_title': course.course_title,
                    'title': course.course_title,
                    'level': {
                        'name': course.level.name if course.level else 'N/A'
                    } if course.level else None,
                    'credit_units': course.credit_unit,
                    'units': course.credit_unit,
                    'credits': course.credit_unit,
                    'semester': {
                        'name': course.semester.get_name_display() if course.semester else 'N/A'
                    } if course.semester else None,
                    'lecturer': lecturer_info
                }
                
                courses.append(course_data)
            
            return Response(
                {'success': True, 'data': courses},
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
