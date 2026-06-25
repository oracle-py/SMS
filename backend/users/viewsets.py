"""
ViewSets for user models.

This module provides ViewSets for StudentProfile, ParentProfile,
and ParentStudentRelation models with proper permissions and filtering.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from users.models import StudentProfile, ParentProfile, ParentStudentRelation
from users.serializers import (
    StudentProfileSerializer,
    StudentProfileDetailSerializer,
    ParentProfileSerializer,
    ParentProfileDetailSerializer,
    ParentStudentRelationSerializer,
    ParentStudentRelationDetailSerializer,
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
        Create student profile with proper validation.
        
        Args:
            serializer: Validated serializer instance
        """
        serializer.save()


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
        Create parent profile with proper validation.
        
        Args:
            serializer: Validated serializer instance
        """
        serializer.save()


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
