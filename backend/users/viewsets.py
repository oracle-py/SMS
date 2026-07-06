"""
ViewSets for user models.

This module provides ViewSets for StudentProfile, ParentProfile,
and ParentStudentRelation models with proper permissions and filtering.
"""

import logging
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from users.models import StudentProfile, ParentProfile, ParentStudentRelation, LecturerProfile
from users.serializers import (
    StudentProfileSerializer,
    StudentProfileDetailSerializer,
    ParentProfileSerializer,
    ParentProfileDetailSerializer,
    ParentStudentRelationSerializer,
    ParentStudentRelationDetailSerializer,
    LecturerProfileSerializer,
    LecturerProfileDetailSerializer,
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
from users.utils.email_utils import (
    send_student_registration_email,
    send_lecturer_registration_email,
    send_parent_registration_email
)

logger = logging.getLogger(__name__)


class StudentProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StudentProfile model.
    
    Provides CRUD operations for student profiles with role-based permissions.
    - Admins: Full access
    - Students: Read-only access to their own profile
    - Parents: Read-only access to linked students' profiles
    """
    
    queryset = StudentProfile.objects.select_related('user').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade_level']
    search_fields = ['student_id', 'user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['student_id', 'grade_level', 'enrollment_date']
    ordering = ['student_id']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        
        Returns:
            Detail serializer for retrieve/update actions, list serializer otherwise
        """
        if self.action in ['retrieve', 'update', 'partial_update']:
            return StudentProfileDetailSerializer
        return StudentProfileSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin or student owner permissions for object access
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrStudentOwner()]
        elif self.action in ['retrieve']:
            return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]
        return [IsAuthenticated(), IsAdminRole()]
    
    def perform_create(self, serializer):
        """
        Create student profile with proper validation and send registration email.
        
        Args:
            serializer: Validated serializer instance
        """
        logger.info("StudentProfileViewSet.perform_create called")
        student = serializer.save()
        logger.info(f"Student created: {student.user.email}, ID: {student.id}")
        
        # Send registration email to personal email (real address)
        try:
            logger.info(f"Attempting to send registration email to personal email: {student.user.email}")
            # Use the default password that was set in the serializer
            default_password = 'school1234'
            send_student_registration_email(
                email=student.user.email,  # Send to personal email (real address)
                first_name=student.user.first_name,
                last_name=student.user.last_name,
                matric_number=student.student_id,
                school_email=student.user.username,  # School email for login
                password=default_password
            )
            logger.info("Registration email sent successfully")
        except Exception as e:
            # Log error but don't fail the registration
            logger.error(f"Failed to send registration email: {e}", exc_info=True)
    
    def perform_destroy(self, instance):
        """
        Delete student profile and associated user from database.
        
        Args:
            instance: StudentProfile instance to delete
        """
        logger.info(f"StudentProfileViewSet.perform_destroy called for ID: {instance.id}")
        # Delete the associated user first, which will cascade to the profile
        if instance.user:
            user_id = instance.user.id
            instance.user.delete()
            logger.info(f"User deleted successfully: {user_id}")
        else:
            instance.delete()
        logger.info(f"Student deleted successfully: {instance.id}")
    
    @action(detail=True, methods=['get'])
    def cgpa(self, request, pk=None):
        """
        Get cumulative CGPA for a student.
        """
        student = self.get_object()
        cgpa = student.calculate_cumulative_cgpa()
        return Response({
            'student_id': student.student_id,
            'student_name': student.user.get_full_name(),
            'cumulative_cgpa': cgpa
        })
    
    @action(detail=True, methods=['get'], url_path='cgpa/session/(?P<session_id>[^/.]+)')
    def session_cgpa(self, request, pk=None, session_id=None):
        """
        Get CGPA for a specific academic session.
        """
        student = self.get_object()
        from academics.models import AcademicSession
        try:
            session = AcademicSession.objects.get(id=session_id)
            cgpa = student.calculate_session_cgpa(session)
            return Response({
                'student_id': student.student_id,
                'student_name': student.user.get_full_name(),
                'session': session.name,
                'session_cgpa': cgpa
            })
        except AcademicSession.DoesNotExist:
            return Response(
                {'detail': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], url_path='cgpa/session/(?P<session_id>[^/.]+)/semester/(?P<semester_id>[^/.]+)')
    def semester_cgpa(self, request, pk=None, session_id=None, semester_id=None):
        """
        Get CGPA for a specific semester.
        """
        student = self.get_object()
        from academics.models import AcademicSession, Semester
        try:
            session = AcademicSession.objects.get(id=session_id)
            semester = Semester.objects.get(id=semester_id)
            cgpa = student.calculate_semester_cgpa(session, semester)
            return Response({
                'student_id': student.student_id,
                'student_name': student.user.get_full_name(),
                'session': session.name,
                'semester': semester.get_name_display(),
                'semester_cgpa': cgpa
            })
        except (AcademicSession.DoesNotExist, Semester.DoesNotExist):
            return Response(
                {'detail': 'Session or semester not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ParentProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ParentProfile model.
    
    Provides CRUD operations for parent profiles with role-based permissions.
    - Admins: Full access
    - Parents: Read-only access to their own profile
    - Students: No access
    """
    
    queryset = ParentProfile.objects.select_related('user').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'occupation']
    ordering_fields = ['user__last_name']
    ordering = ['user__last_name']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        
        Returns:
            Detail serializer for retrieve/update actions, list serializer otherwise
        """
        if self.action in ['retrieve', 'update', 'partial_update']:
            return ParentProfileDetailSerializer
        return ParentProfileSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin-only permissions for most actions
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated(), IsAdminRole()]
    
    def perform_create(self, serializer):
        """
        Create parent profile with proper validation and send registration email.
        
        Args:
            serializer: Validated serializer instance
        """
        parent = serializer.save()
        logger.info(f"Parent created: {parent.user.email}, ID: {parent.id}")
        
        # Send registration email to personal email (real address)
        try:
            logger.info(f"Attempting to send registration email to personal email: {parent.user.email}")
            # Get linked student if available
            child_name = None
            child_matric = None
            relation = parent.parentstudentrelation_set.first()
            if relation and relation.student:
                child_name = f"{relation.student.user.first_name} {relation.student.user.last_name}"
                child_matric = relation.student.student_id
            
            # Use the default password that should be set in the serializer
            default_password = 'school1234'
            send_parent_registration_email(
                email=parent.user.email,  # Send to personal email (real address)
                first_name=parent.user.first_name,
                last_name=parent.user.last_name,
                password=default_password,
                child_name=child_name,
                child_matric=child_matric,
                school_email=parent.user.username  # School email for login
            )
            logger.info("Registration email sent successfully")
        except Exception as e:
            # Log error but don't fail the registration
            logger.error(f"Failed to send registration email: {e}", exc_info=True)
    
    def perform_destroy(self, instance):
        """
        Delete parent profile and associated user from database.
        
        Args:
            instance: ParentProfile instance to delete
        """
        logger.info(f"ParentProfileViewSet.perform_destroy called for ID: {instance.id}")
        # Delete the associated user first, which will cascade to the profile
        if instance.user:
            user_id = instance.user.id
            instance.user.delete()
            logger.info(f"User deleted successfully: {user_id}")
        else:
            instance.delete()
        logger.info(f"Parent deleted successfully: {instance.id}")


class ParentStudentRelationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ParentStudentRelation model.
    
    Provides CRUD operations for parent-student relationships with role-based permissions.
    - Admins: Full access
    - Parents: Full access to their own relationships
    - Students: Read-only access to their own relationships
    """
    
    queryset = ParentStudentRelation.objects.select_related(
        'parent__user', 'student__user'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['relationship_type']
    search_fields = [
        'parent__user__username',
        'parent__user__first_name',
        'parent__user__last_name',
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'student__student_id'
    ]
    ordering_fields = ['relationship_type']
    ordering = ['relationship_type']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        
        Returns:
            Detail serializer for retrieve/update actions, list serializer otherwise
        """
        if self.action in ['retrieve', 'update', 'partial_update']:
            return ParentStudentRelationDetailSerializer
        return ParentStudentRelationSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin or parent-linked permissions for object access
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]
        elif self.action in ['retrieve']:
            return [IsAuthenticated(), IsAdminOrParentLinkedToStudent()]
        return [IsAuthenticated(), IsAdminRole()]
    
    def perform_create(self, serializer):
        """
        Create parent-student relationship with proper validation.
        
        Args:
            serializer: Validated serializer instance
        """
        serializer.save()


class LecturerProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LecturerProfile model.
    
    Provides CRUD operations for lecturer profiles with role-based permissions.
    - Admins: Full access
    - Lecturers: Read-only access to their own profile
    - Others: Read-only access
    """
    
    queryset = LecturerProfile.objects.select_related('user', 'department', 'department__faculty').all()
    serializer_class = LecturerProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rank', 'employment_type', 'department']
    search_fields = ['staff_id', 'user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['staff_id', 'date_of_employment']
    ordering = ['staff_id']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        
        Returns:
            Detail serializer for retrieve action, list serializer otherwise
        """
        if self.action == 'retrieve':
            return LecturerProfileDetailSerializer
        return LecturerProfileSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        
        Returns:
            Admin or lecturer owner permissions for object access
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """
        Create lecturer profile with proper validation and send registration email.
        
        Args:
            serializer: Validated serializer instance
        """
        lecturer = serializer.save()
        logger.info(f"Lecturer created: {lecturer.user.email}, ID: {lecturer.id}")
        
        # Send registration email to personal email (real address)
        try:
            logger.info(f"Attempting to send registration email to personal email: {lecturer.user.email}")
            # Use the default password that was set in the serializer
            default_password = 'school1234'
            send_lecturer_registration_email(
                email=lecturer.user.email,  # Send to personal email (real address)
                first_name=lecturer.user.first_name,
                last_name=lecturer.user.last_name,
                staff_id=lecturer.staff_id,
                department=lecturer.department.name if lecturer.department else 'Not Assigned',
                rank=lecturer.rank if lecturer.rank else 'Not Assigned',
                password=default_password,
                school_email=lecturer.user.username  # School email for login
            )
            logger.info("Registration email sent successfully")
        except Exception as e:
            # Log error but don't fail the registration
            logger.error(f"Failed to send registration email: {e}", exc_info=True)
    
    def perform_destroy(self, instance):
        """
        Delete lecturer profile and associated user from database.
        
        Args:
            instance: LecturerProfile instance to delete
        """
        logger.info(f"LecturerProfileViewSet.perform_destroy called for ID: {instance.id}")
        # Delete the associated user first, which will cascade to the profile
        if instance.user:
            user_id = instance.user.id
            instance.user.delete()
            logger.info(f"User deleted successfully: {user_id}")
        else:
            instance.delete()
        logger.info(f"Lecturer deleted successfully: {instance.id}")
