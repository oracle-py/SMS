"""
Public statistics view for login page.

This module provides public statistics (student count, lecturer count, trust score)
for the login page without requiring authentication.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count

from users.models import User, StudentProfile, LecturerProfile


class PublicStatsView(APIView):
    """
    Public statistics endpoint.
    
    Returns public statistics for the login page including:
    - Total number of students
    - Total number of lecturers
    - Trust score (placeholder)
    """
    
    permission_classes = []  # No authentication required
    
    def get(self, request) -> Response:
        """
        Get public statistics.
        
        Returns:
            Response with public statistics data
        """
        try:
            # Count students
            student_count = StudentProfile.objects.count()
            
            # Count lecturers
            lecturer_count = LecturerProfile.objects.count()
            
            # Trust score (placeholder - could be calculated from actual metrics)
            trust_score = "95%"
            
            response_data = {
                'students': student_count,
                'lecturers': lecturer_count,
                'trust_score': trust_score
            }
            
            return Response(
                response_data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
