"""
ViewSets for academic models.

This module provides ViewSets for academic models including
sessions, semesters, levels, courses, enrollments, registrations,
grades, and attendance with proper permissions and filtering.
"""

import logging
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from academics.utils import log_activity

logger = logging.getLogger(__name__)


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

from academics.models import (
    AcademicSession,
    Semester,
    Level,
    Course,
    StudentEnrollment,
    CourseRegistration,
    Grade,
    Attendance,
    Faculty,
    Department,
    Programme,
    CourseAssignment,
    Timetable,
    Announcement,
    Result,
    ActivityLog,
)
from academics.serializers import (
    AcademicSessionSerializer,
    SemesterSerializer,
    LevelSerializer,
    CourseSerializer,
    StudentEnrollmentSerializer,
    CourseRegistrationSerializer,
    CourseRegistrationDetailSerializer,
    GradeSerializer,
    GradeDetailSerializer,
    AttendanceSerializer,
    AttendanceDetailSerializer,
    FacultySerializer,
    DepartmentSerializer,
    ProgrammeSerializer,
    CourseAssignmentSerializer,
    TimetableSerializer,
    AnnouncementSerializer,
    ResultSerializer,
    BatchResultSerializer,
    ActivityLogSerializer,
)
from users.permissions import (
    IsAdminRole,
    IsStudentRole,
    IsParentRole,
    IsStudentOwner,
    IsParentLinkedToStudent,
    IsAdminOrStudentOwner,
    IsAdminOrParentLinkedToStudent,
    IsAdminOrReadOnly,
)


class AcademicSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AcademicSession model.
    
    Provides CRUD operations for academic sessions.
    - Admins: Full access
    - Students/Parents: Read-only access
    """
    
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['-name']
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin-only for write operations, read-only for others
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]


class SemesterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Semester model.
    
    Provides CRUD operations for semesters.
    - Admins: Full access
    - Students/Parents: Read-only access
    """
    
    queryset = Semester.objects.select_related('session').all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'session']
    search_fields = ['name', 'session__name']
    ordering_fields = ['name']
    ordering = ['session', 'name']
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin-only for write operations, read-only for others
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]


class LevelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Level model.
    
    Provides CRUD operations for academic levels.
    - Admins: Full access
    - Students/Parents: Read-only access
    """
    
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin-only for write operations, read-only for others
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course model.
    
    Provides CRUD operations for courses.
    - Admins: Full access
    - Students/Parents: Read-only access
    """
    
    queryset = Course.objects.select_related('level', 'semester', 'semester__session').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'semester', 'credit_unit', 'is_active']
    search_fields = ['course_code', 'course_title']
    ordering_fields = ['course_code', 'course_title', 'credit_unit']
    ordering = ['course_code']
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin-only for write operations, read-only for others
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """
        Create course and log activity.
        
        Args:
            serializer: Validated serializer instance
        """
        course = serializer.save()
        
        # Log activity
        try:
            log_activity(
                user=self.request.user,
                action='CREATE_COURSE',
                entity_type='Course',
                entity_id=course.id,
                description=f"Created course {course.course_code}: {course.course_title}",
                ip_address=get_client_ip(self.request)
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)
    
    def perform_destroy(self, instance):
        """
        Delete course and log activity.
        
        Args:
            instance: Course instance to delete
        """
        # Log activity before deletion
        try:
            log_activity(
                user=self.request.user,
                action='DELETE_COURSE',
                entity_type='Course',
                entity_id=instance.id,
                description=f"Deleted course {instance.course_code}: {instance.course_title}",
                ip_address=get_client_ip(self.request)
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)
        
        instance.delete()


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StudentEnrollment model.
    
    Provides CRUD operations for student enrollments.
    - Admins: Full access
    - Students: Read-only access to their own enrollments
    - Parents: Read-only access to linked students' enrollments
    """
    
    queryset = StudentEnrollment.objects.select_related(
        'student__user', 'session', 'level'
    ).all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['session', 'level']
    search_fields = [
        'student__student_id',
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'session__name'
    ]
    ordering_fields = ['enrollment_date', 'session__name']
    ordering = ['-enrollment_date']
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin or student owner permissions for object access
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        elif self.action in ['retrieve']:
            return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]
        return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]


class CourseRegistrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CourseRegistration model.
    
    Provides CRUD operations for course registrations.
    - Admins: Full access
    - Students: Read-only access to their own registrations
    - Parents: Read-only access to linked students' registrations
    """
    
    queryset = CourseRegistration.objects.select_related(
        'student__user', 'course', 'session', 'semester'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['session', 'semester', 'course', 'is_carryover']
    search_fields = [
        'student__student_id',
        'student__user__username',
        'course__course_code',
        'course__course_title',
        'session__name'
    ]
    ordering_fields = ['registration_date', 'course__course_code']
    ordering = ['-registration_date']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        
        Returns:
            Detail serializer for retrieve action, list serializer otherwise
        """
        if self.action == 'retrieve':
            return CourseRegistrationDetailSerializer
        return CourseRegistrationSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin or student owner permissions for object access
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        elif self.action in ['retrieve']:
            return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]
        return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]


class GradeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Grade model.
    
    Provides CRUD operations for grades.
    - Admins: Full access
    - Students: Read-only access to their own grades
    - Parents: Read-only access to linked students' grades
    """
    
    queryset = Grade.objects.select_related(
        'registration__student__user',
        'registration__course',
        'registration__session',
        'registration__semester'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['letter_grade', 'grade_point']
    search_fields = [
        'registration__student__student_id',
        'registration__student__user__username',
        'registration__course__course_code',
        'registration__course__course_title',
        'registration__session__name'
    ]
    ordering_fields = ['updated_at', 'score']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        
        Returns:
            Detail serializer for retrieve action, list serializer otherwise
        """
        if self.action == 'retrieve':
            return GradeDetailSerializer
        return GradeSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin or student owner permissions for object access
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        elif self.action in ['retrieve']:
            return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]
        return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attendance model.
    
    Provides CRUD operations for attendance records.
    - Admins: Full access
    - Students: Read-only access to their own attendance
    - Parents: Read-only access to linked students' attendance
    """
    
    queryset = Attendance.objects.select_related(
        'student__user', 'course'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'date', 'course']
    search_fields = [
        'student__student_id',
        'student__user__username',
        'course__course_code',
        'course__course_title'
    ]
    ordering_fields = ['date', 'status']
    ordering = ['-date']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        
        Returns:
            Detail serializer for retrieve action, list serializer otherwise
        """
        if self.action == 'retrieve':
            return AttendanceDetailSerializer
        return AttendanceSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin or student owner permissions for object access
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        elif self.action == 'batch':
            return [IsAuthenticated()]  # Allow all authenticated users for batch operations
        elif self.action == 'retrieve':
            return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]
        return [IsAuthenticated()]  # Allow all authenticated users for list

    @action(detail=False, methods=['post'], url_path='batch')
    def batch(self, request):
        """
        Batch create or update attendance records.

        Accepts data with date, course_id, and attendance array.
        For each attendance record in the array, creates or updates Attendance records.

        Request body:
        {
            "date": "2025-01-15",
            "course_id": 1,
            "attendance": [
                {"student_id": 1, "present": true},
                {"student_id": 2, "present": false}
            ]
        }

        Returns:
            Response with success message and number of records processed
        """
        from users.models import StudentProfile

        data = request.data
        date_str = data.get('date')
        course_id = data.get('course_id')
        attendance_data = data.get('attendance', [])

        # Validate required fields
        if not date_str:
            return Response(
                {'error': 'Date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not course_id:
            return Response(
                {'error': 'Course ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not attendance_data:
            return Response(
                {'error': 'Attendance array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse date
        try:
            from datetime import datetime
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get course
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is lecturer assigned to this course
        if request.user.role == 'lecturer':
            from academics.models import CourseAssignment
            has_assignment = CourseAssignment.objects.filter(
                lecturer=request.user,
                course=course
            ).exists()
            if not has_assignment:
                return Response(
                    {'error': 'You are not assigned to teach this course'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Process attendance records
        records_processed = 0
        errors = []

        for record in attendance_data:
            student_id = record.get('student_id')
            present = record.get('present')

            if not student_id or present is None:
                errors.append(f"Invalid record: student_id and present are required")
                continue

            try:
                student_profile = StudentProfile.objects.get(id=student_id)
                student_user = student_profile.user
            except StudentProfile.DoesNotExist:
                errors.append(f"Student with ID {student_id} not found")
                continue

            # Convert boolean to status
            status_value = 'present' if present else 'absent'

            # Create or update attendance record
            try:
                attendance, created = Attendance.objects.update_or_create(
                    student=student_profile,
                    course=course,
                    date=attendance_date,
                    defaults={
                        'status': status_value,
                        'recorded_by': request.user,
                        'recorded_at': timezone.now()
                    }
                )
                records_processed += 1
            except Exception as e:
                errors.append(f"Failed to process attendance for student {student_id}: {str(e)}")

        # Log activity
        try:
            log_activity(
                user=request.user,
                action='BATCH_ATTENDANCE',
                entity_type='Attendance',
                entity_id=course_id,
                description=f"Batch processed {records_processed} attendance records for course {course.course_code} on {attendance_date}",
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)

        # Return response
        response_data = {
            'message': f'Successfully processed {records_processed} attendance records',
            'records_processed': records_processed,
            'date': date_str,
            'course_id': course_id
        }

        if errors:
            response_data['errors'] = errors

        return Response(response_data, status=status.HTTP_200_OK)


class FacultyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Faculty model.
    
    Provides CRUD operations for faculties.
    - Admins: Full access
    - Others: Read-only access
    """
    
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name']
    ordering = ['name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department model.
    
    Provides CRUD operations for departments.
    - Admins: Full access
    - Others: Read-only access
    """
    
    queryset = Department.objects.select_related('faculty').all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['faculty']
    search_fields = ['name', 'code', 'faculty__name']
    ordering_fields = ['name', 'faculty']
    ordering = ['faculty', 'name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]


class ProgrammeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Programme model.
    
    Provides CRUD operations for programmes.
    - Admins: Full access
    - Others: Read-only access
    """
    
    queryset = Programme.objects.select_related('department', 'department__faculty').all()
    serializer_class = ProgrammeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department']
    search_fields = ['name', 'code', 'department__name']
    ordering_fields = ['name', 'department']
    ordering = ['department', 'name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]


class CourseAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CourseAssignment model.
    
    Provides CRUD operations for course assignments.
    - Admins: Full access
    - Lecturers: Read-only access to their assignments
    - Others: Read-only access
    """
    
    queryset = CourseAssignment.objects.select_related(
        'course', 'lecturer', 'session', 'semester'
    ).all()
    serializer_class = CourseAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'lecturer', 'session', 'semester', 'role']
    search_fields = ['course__course_code', 'lecturer__username']
    ordering_fields = ['session', 'semester', 'course']
    ordering = ['session', 'semester', 'course']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]


class TimetableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Timetable model.
    
    Provides CRUD operations for timetables.
    - Admins: Full access
    - Others: Read-only access
    """
    
    queryset = Timetable.objects.select_related(
        'course_assignment__course', 'course_assignment__lecturer', 'session', 'semester'
    ).all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['day_of_week', 'session', 'semester']
    search_fields = ['course_assignment__course__course_code', 'venue']
    ordering_fields = ['day_of_week', 'start_time']
    ordering = ['day_of_week', 'start_time']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Announcement model.
    
    Provides CRUD operations for announcements.
    - Admins: Full access
    - Others: Read-only access to announcements targeting their role
    """
    
    queryset = Announcement.objects.select_related('created_by').all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_audience', 'is_active']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by target audience
        if not user.is_admin_user:
            audience_map = {
                'student': 'student',
                'lecturer': 'lecturer',
                'parent': 'parent',
            }
            user_audience = audience_map.get(user.role, 'all')
            from django.db import models as django_models
            queryset = queryset.filter(
                django_models.Q(target_audience='all') | django_models.Q(target_audience=user_audience)
            )
        
        return queryset.filter(is_active=True)


class ResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Result model.
    
    Provides CRUD operations for student results.
    - Admins: Full access including approval
    - Lecturers: Can create and view their submitted results
    - Students: Can only view their own approved results
    - Parents: Can only view their children's approved results
    """
    
    queryset = Result.objects.select_related(
        'student', 'course', 'lecturer', 'session', 'semester', 'approved_by'
    ).all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'lecturer', 'session', 'semester', 'status']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'course__course_code']
    ordering_fields = ['submitted_at', 'approved_at', 'total_score']
    ordering = ['-submitted_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_admin_user:
            return queryset
        elif user.is_lecturer:
            # Lecturers can see results they submitted (including drafts)
            return queryset.filter(lecturer=user)
        elif user.is_student:
            # Students can only see their own approved results
            return queryset.filter(student=user, status='approved')
        elif user.is_parent:
            # Parents can see their children's approved results
            from users.models import ParentStudentRelation
            child_ids = ParentStudentRelation.objects.filter(
                parent=user.parent_profile
            ).values_list('student__user_id', flat=True)
            return queryset.filter(student_id__in=child_ids, status='approved')
        return queryset.none()
    
    @action(detail=False, methods=['post'])
    def batch(self, request):
        """
        Batch create results for multiple students.
        Used by lecturers to submit results for a course.
        """
        serializer = BatchResultSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result_data = serializer.save()
            
            # Log activity
            try:
                from academics.models import Course
                course_id = request.data.get('course_id')
                course = Course.objects.get(id=course_id)
                action = result_data.get('action', 'submit')
                
                action_text = 'Saved draft' if action == 'save' else 'Submitted'
                log_activity(
                    user=request.user,
                    action='BATCH_RESULTS',
                    entity_type='Result',
                    entity_id=course.id,
                    description=f"{action_text} results for {len(result_data['results'])} students in {course.course_code}",
                    ip_address=get_client_ip(request)
                )
            except Exception as e:
                logger.error(f"Failed to log activity: {e}", exc_info=True)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a result (admin only).
        """
        result = self.get_object()
        if not request.user.is_admin_user:
            return Response(
                {'detail': 'Only admins can approve results'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result.status = 'approved'
        result.approved_by = request.user
        result.approved_at = timezone.now()
        result.save()
        
        # Log activity
        try:
            log_activity(
                user=request.user,
                action='APPROVE_RESULT',
                entity_type='Result',
                entity_id=result.id,
                description=f"Approved result for {result.student.username} in {result.course.course_code}",
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)
        
        return Response({'detail': 'Result approved successfully'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a result (admin only).
        """
        result = self.get_object()
        if not request.user.is_admin_user:
            return Response(
                {'detail': 'Only admins can reject results'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result.status = 'rejected'
        result.remarks = request.data.get('remarks', '')
        result.save()
        
        # Log activity
        try:
            log_activity(
                user=request.user,
                action='REJECT_RESULT',
                entity_type='Result',
                entity_id=result.id,
                description=f"Rejected result for {result.student.username} in {result.course.course_code}",
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}", exc_info=True)
        
        return Response({'detail': 'Result rejected successfully'})


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ActivityLog model.
    
    Provides read-only access to activity logs.
    - Admins: Can see all activity logs
    - Other users: Can only see their own activity logs
    """
    
    queryset = ActivityLog.objects.select_related('user').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'entity_type']
    search_fields = ['description', 'action']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_admin_user:
            return queryset
        else:
            # Non-admin users can only see their own activity logs
            return queryset.filter(user=user)
