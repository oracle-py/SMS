"""
Custom permissions for the student monitoring system.

This module provides role-based and object-level permissions
for controlling access to API endpoints.
"""

from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsAdminRole(permissions.BasePermission):
    """
    Permission to only allow users with admin role.
    
    Grants access only to users whose role is 'admin'.
    """
    
    def has_permission(self, request: Request, view: View) -> bool:
        """
        Check if user has admin role.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            
        Returns:
            True if user is authenticated and has admin role, False otherwise
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsStudentRole(permissions.BasePermission):
    """
    Permission to only allow users with student role.
    
    Grants access only to users whose role is 'student'.
    """
    
    def has_permission(self, request: Request, view: View) -> bool:
        """
        Check if user has student role.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            
        Returns:
            True if user is authenticated and has student role, False otherwise
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'student'
        )


class IsParentRole(permissions.BasePermission):
    """
    Permission to only allow users with parent role.
    
    Grants access only to users whose role is 'parent'.
    """
    
    def has_permission(self, request: Request, view: View) -> bool:
        """
        Check if user has parent role.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            
        Returns:
            True if user is authenticated and has parent role, False otherwise
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'parent'
        )


class IsStudentOwner(permissions.BasePermission):
    """
    Object-level permission to only allow students to access their own data.
    
    Grants access only if the authenticated student is the owner of the object.
    """
    
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Check if user is the owner of the object.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            obj: The object being accessed
            
        Returns:
            True if user is authenticated student and owns the object, False otherwise
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'student' and
            getattr(obj, 'student', None) == request.user.student_profile
        )


class IsParentLinkedToStudent(permissions.BasePermission):
    """
    Object-level permission to only allow parents to access their linked students' data.
    
    Grants access only if the authenticated parent is linked to the student in the object.
    """
    
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Check if parent is linked to the student in the object.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            obj: The object being accessed
            
        Returns:
            True if user is authenticated parent and linked to the student, False otherwise
        """
        if not (request.user and request.user.is_authenticated and request.user.role == 'parent'):
            return False
        
        try:
            parent_profile = request.user.parent_profile
            student = getattr(obj, 'student', None)
            
            if not student:
                return False
            
            # Check if parent is linked to this student
            from users.models import ParentStudentRelation
            return ParentStudentRelation.objects.filter(
                parent=parent_profile,
                student=student
            ).exists()
        except Exception:
            return False


class IsAdminOrStudentOwner(permissions.BasePermission):
    """
    Permission to allow admins or the student owner to access the object.
    
    Grants access to admins or the student who owns the object.
    """
    
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Check if user is admin or the owner of the object.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            obj: The object being accessed
            
        Returns:
            True if user is admin or student owner, False otherwise
        """
        # Admins have full access
        if request.user and request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # Students can only access their own data
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'student' and
            getattr(obj, 'student', None) == request.user.student_profile
        )


class IsAdminOrParentLinkedToStudent(permissions.BasePermission):
    """
    Permission to allow admins or parents linked to the student to access the object.
    
    Grants access to admins or parents linked to the student in the object.
    """
    
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Check if user is admin or parent linked to the student.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            obj: The object being accessed
            
        Returns:
            True if user is admin or parent linked to student, False otherwise
        """
        # Admins have full access
        if request.user and request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # Parents can only access their linked students' data
        if not (request.user and request.user.is_authenticated and request.user.role == 'parent'):
            return False
        
        try:
            parent_profile = request.user.parent_profile
            student = getattr(obj, 'student', None)
            
            if not student:
                return False
            
            from users.models import ParentStudentRelation
            return ParentStudentRelation.objects.filter(
                parent=parent_profile,
                student=student
            ).exists()
        except Exception:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow admins full access and others read-only access.
    
    Grants full access to admins, read-only access to authenticated users.
    """
    
    def has_permission(self, request: Request, view: View) -> bool:
        """
        Check if user has appropriate permissions.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            
        Returns:
            True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Check if user has appropriate permissions for the object.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            obj: The object being accessed
            
        Returns:
            True if admin or read-only request, False otherwise
        """
        # Admins have full access
        if request.user and request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # Read-only access for authenticated users
        return request.method in permissions.SAFE_METHODS
