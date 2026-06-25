"""
Standardized API response serializers.

This module provides consistent response structures for all API endpoints,
ensuring a uniform API contract for frontend integration.
"""

from rest_framework import serializers


class SuccessResponseSerializer(serializers.Serializer):
    """
    Standard success response wrapper.
    
    Provides a consistent structure for all successful API responses.
    """
    success = serializers.BooleanField(default=True, read_only=True)
    data = serializers.DictField(required=False, read_only=True)
    message = serializers.CharField(required=False, allow_blank=True, read_only=True)


class ErrorResponseSerializer(serializers.Serializer):
    """
    Standard error response wrapper.
    
    Provides a consistent structure for all error responses.
    """
    success = serializers.BooleanField(default=False, read_only=True)
    error = serializers.CharField(read_only=True)
    details = serializers.DictField(required=False, read_only=True)


class StudentInfoSerializer(serializers.Serializer):
    """Serializer for student information in dashboard."""
    name = serializers.CharField(read_only=True)
    matric_number = serializers.CharField(read_only=True)
    level = serializers.CharField(read_only=True)


class RecentResultSerializer(serializers.Serializer):
    """Serializer for recent results in dashboard."""
    course_code = serializers.CharField(read_only=True)
    course_title = serializers.CharField(read_only=True)
    score = serializers.FloatField(read_only=True)
    grade = serializers.CharField(read_only=True)
    session = serializers.CharField(read_only=True)
    semester = serializers.CharField(read_only=True)


class StudentDashboardSerializer(serializers.Serializer):
    """
    Serializer for student dashboard response.
    
    Provides comprehensive academic summary for the authenticated student.
    """
    student_info = StudentInfoSerializer(read_only=True)
    cgpa = serializers.FloatField(read_only=True)
    academic_standing = serializers.CharField(read_only=True)
    attendance_percentage = serializers.FloatField(read_only=True)
    carryover_count = serializers.IntegerField(read_only=True)
    total_courses_registered = serializers.IntegerField(read_only=True)
    recent_results = RecentResultSerializer(many=True, read_only=True)


class StudentResultSerializer(serializers.Serializer):
    """
    Serializer for student results response.
    
    Provides detailed grade information for the authenticated student.
    """
    course_code = serializers.CharField(read_only=True)
    course_title = serializers.CharField(read_only=True)
    score = serializers.FloatField(read_only=True)
    letter_grade = serializers.CharField(read_only=True)
    grade_point = serializers.IntegerField(read_only=True)
    session = serializers.CharField(read_only=True)
    semester = serializers.CharField(read_only=True)
    credit_unit = serializers.IntegerField(read_only=True)


class AttendanceRecordSerializer(serializers.Serializer):
    """Serializer for individual attendance record."""
    course = serializers.CharField(read_only=True)
    course_title = serializers.CharField(read_only=True)
    date = serializers.DateField(read_only=True)
    status = serializers.CharField(read_only=True)
    remarks = serializers.CharField(required=False, allow_blank=True, read_only=True)


class StudentAttendanceSerializer(serializers.Serializer):
    """
    Serializer for student attendance response.
    
    Provides attendance records and statistics for the authenticated student.
    """
    attendance_percentage = serializers.FloatField(read_only=True)
    total_records = serializers.IntegerField(read_only=True)
    present_records = serializers.IntegerField(read_only=True)
    absent_records = serializers.IntegerField(read_only=True)
    records = AttendanceRecordSerializer(many=True, read_only=True)


class WardInfoSerializer(serializers.Serializer):
    """Serializer for ward (student) information in parent dashboard."""
    student_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    matric_number = serializers.CharField(read_only=True)
    level = serializers.CharField(read_only=True)
    cgpa = serializers.FloatField(read_only=True)
    academic_standing = serializers.CharField(read_only=True)
    attendance_percentage = serializers.FloatField(read_only=True)
    carryover_count = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    relationship_type = serializers.CharField(read_only=True)


class ParentDashboardSerializer(serializers.Serializer):
    """
    Serializer for parent dashboard response.
    
    Provides overview of all students linked to the authenticated parent.
    """
    parent_name = serializers.CharField(read_only=True)
    total_wards = serializers.IntegerField(read_only=True)
    wards = WardInfoSerializer(many=True, read_only=True)


class WardDetailInfoSerializer(serializers.Serializer):
    """Serializer for detailed ward information."""
    student_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    matric_number = serializers.CharField(read_only=True)
    level = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class CarryoverSerializer(serializers.Serializer):
    """Serializer for carryover course information."""
    course_code = serializers.CharField(read_only=True)
    course_title = serializers.CharField(read_only=True)
    score = serializers.FloatField(read_only=True)
    letter_grade = serializers.CharField(read_only=True)
    session = serializers.CharField(read_only=True)
    semester = serializers.CharField(read_only=True)


class ParentWardSerializer(serializers.Serializer):
    """
    Serializer for parent ward detail response.
    
    Provides detailed academic information for a specific linked student.
    """
    student_info = WardDetailInfoSerializer(read_only=True)
    cgpa = serializers.FloatField(read_only=True)
    academic_standing = serializers.CharField(read_only=True)
    attendance_percentage = serializers.FloatField(read_only=True)
    carryover_count = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    relationship_type = serializers.CharField(read_only=True)
    results = StudentResultSerializer(many=True, read_only=True)
    carryovers = CarryoverSerializer(many=True, read_only=True)
    attendance_records = AttendanceRecordSerializer(many=True, read_only=True)


class LogoutRequestSerializer(serializers.Serializer):
    """Serializer for logout request."""
    refresh_token = serializers.CharField(required=True, write_only=True)


class LogoutResponseSerializer(serializers.Serializer):
    """Serializer for logout response."""
    success = serializers.BooleanField(default=True, read_only=True)
    message = serializers.CharField(read_only=True)


class CurrentUserResponseSerializer(serializers.Serializer):
    """Serializer for current user response."""
    success = serializers.BooleanField(default=True, read_only=True)
    data = serializers.DictField(read_only=True)
