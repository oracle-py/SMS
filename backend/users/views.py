"""
Authentication views for the student monitoring system.

This module provides views for JWT-based authentication including
login, token refresh, logout, and current user information.
"""

from typing import Dict, Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from users.serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    StudentProfileSerializer,
    ParentProfileSerializer,
)
from api.serializers import (
    LogoutRequestSerializer,
    LogoutResponseSerializer,
    CurrentUserResponseSerializer,
    ErrorResponseSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view with enhanced response.
    
    Returns JWT tokens along with user and profile information.
    """
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view.
    
    Handles token refresh requests with proper error handling.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle token refresh with proper error handling for deleted users.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response with new tokens or error message
        """
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            # Handle case where user no longer exists
            if 'does not exist' in str(e).lower():
                return Response(
                    {'success': False, 'error': 'User account no longer exists. Please log in again.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            # Re-raise other exceptions
            raise


class LogoutView(GenericAPIView):
    """
    Logout view to blacklist the refresh token.
    
    Handles token blacklisting for secure logout.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutRequestSerializer
    
    @extend_schema(
        request=LogoutRequestSerializer,
        responses={
            200: LogoutResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    
    def post(self, request) -> Response:
        """
        Logout by blacklisting the refresh token.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response indicating successful logout or error
        """
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response(
                    {'success': False, 'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'success': True, 'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except (TokenError, InvalidToken) as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': 'An error occurred during logout.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CurrentUserView(GenericAPIView):
    """
    Get current user information with profile data.
    
    Returns authenticated user details including profile information.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    @extend_schema(
        responses={
            200: CurrentUserResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    
    def get(self, request) -> Response:
        """
        Get current user information with profile data.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response with user and profile information
        """
        try:
            user = request.user
            user_data = UserSerializer(user).data
            
            # Add profile information based on role
            if user.role == 'student' and hasattr(user, 'student_profile'):
                user_data['profile'] = StudentProfileSerializer(user.student_profile).data
            elif user.role == 'parent' and hasattr(user, 'parent_profile'):
                user_data['profile'] = ParentProfileSerializer(user.parent_profile).data
            else:
                user_data['profile'] = None
            
            return Response(
                {'success': True, 'data': user_data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
