"""
ViewSets for academic models.

This module provides ViewSets for academic models including
sessions, semesters, levels, courses, enrollments, registrations,
grades, and attendance with proper permissions and filtering.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

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
    filterset_fields = ['session', 'semester', 'is_carryover']
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
    filterset_fields = ['status', 'date']
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
        elif self.action in ['retrieve']:
            return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]
        return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]


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
