"""
Serializers for academic models.

This module provides serializers for all academic models including
sessions, semesters, levels, courses, enrollments, registrations,
grades, and attendance with proper validation and nested relationships.
"""

from datetime import date
from typing import Dict, Any, Optional

from rest_framework import serializers

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
    CGPARecord,
)
from users.models import StudentProfile
from users.serializers import StudentProfileSerializer, StudentProfileDetailSerializer


class AcademicSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for AcademicSession model.
    
    Handles academic session management with validation.
    """
    
    is_active_display = serializers.CharField(source='get_is_active_display', read_only=True)
    
    class Meta:
        model = AcademicSession
        fields = [
            'id',
            'name',
            'start_date',
            'end_date',
            'is_active',
            'is_active_display'
        ]
        read_only_fields = ['id', 'is_active_display']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that end_date is after start_date.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If end_date is before start_date
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {'end_date': 'End date must be after start date.'}
            )
        
        return attrs


class SemesterSerializer(serializers.ModelSerializer):
    """
    Serializer for Semester model.
    
    Includes nested session information.
    """
    
    session = AcademicSessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True)
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = Semester
        fields = [
            'id',
            'name',
            'name_display',
            'session',
            'session_id'
        ]
        read_only_fields = ['id', 'name_display']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that semester is properly linked to a session.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If session is not found
        """
        session_id = attrs.get('session_id')
        
        if session_id:
            try:
                AcademicSession.objects.get(pk=session_id)
            except AcademicSession.DoesNotExist:
                raise serializers.ValidationError(
                    {'session_id': 'Academic session not found.'}
                )
        
        return attrs


class LevelSerializer(serializers.ModelSerializer):
    """
    Serializer for Level model.
    
    Handles academic level management.
    """
    
    class Meta:
        model = Level
        fields = [
            'id',
            'name'
        ]
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model.
    
    Includes nested level and semester information.
    """
    
    level = LevelSerializer(read_only=True)
    level_id = serializers.IntegerField(write_only=True)
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id',
            'course_code',
            'course_title',
            'credit_unit',
            'level',
            'level_id',
            'semester',
            'semester_id',
            'is_active'
        ]
        read_only_fields = ['id']
    
    def validate_course_code(self, value: str) -> str:
        """
        Validate course code uniqueness.
        
        Args:
            value: Course code to validate
            
        Returns:
            Validated course code
            
        Raises:
            ValidationError: If course code already exists
        """
        queryset = Course.objects.filter(course_code=value)
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError('A course with this code already exists.')
        
        return value


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for StudentEnrollment model.
    
    Handles student enrollment in academic sessions.
    """
    
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    session = AcademicSessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True)
    level = LevelSerializer(read_only=True)
    level_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = StudentEnrollment
        fields = [
            'id',
            'student',
            'student_id',
            'session',
            'session_id',
            'level',
            'level_id',
            'enrollment_date'
        ]
        read_only_fields = ['id', 'enrollment_date']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that enrollment doesn't already exist.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If enrollment already exists
        """
        student_id = attrs.get('student_id')
        session_id = attrs.get('session_id')
        
        queryset = StudentEnrollment.objects.filter(
            student_id=student_id,
            session_id=session_id
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'Student is already enrolled in this session.'
            )
        
        return attrs


class CourseRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for CourseRegistration model.
    
    Handles course registration with nested relationships.
    """
    
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    session = AcademicSessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True)
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.IntegerField(write_only=True)
    is_carryover_display = serializers.CharField(
        source='get_is_carryover_display',
        read_only=True
    )
    
    class Meta:
        model = CourseRegistration
        fields = [
            'id',
            'student',
            'student_id',
            'course',
            'course_id',
            'session',
            'session_id',
            'semester',
            'semester_id',
            'registration_date',
            'is_carryover',
            'is_carryover_display'
        ]
        read_only_fields = ['id', 'registration_date', 'is_carryover_display']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that registration doesn't already exist.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If registration already exists
        """
        student_id = attrs.get('student_id')
        course_id = attrs.get('course_id')
        session_id = attrs.get('session_id')
        semester_id = attrs.get('semester_id')
        
        queryset = CourseRegistration.objects.filter(
            student_id=student_id,
            course_id=course_id,
            session_id=session_id,
            semester_id=semester_id
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'Student is already registered for this course in this session/semester.'
            )
        
        return attrs


class CourseRegistrationDetailSerializer(CourseRegistrationSerializer):
    """
    Detailed serializer for CourseRegistration with full nested information.
    """
    
    student = StudentProfileDetailSerializer(read_only=True)
    
    class Meta(CourseRegistrationSerializer.Meta):
        fields = CourseRegistrationSerializer.Meta.fields


class GradeSerializer(serializers.ModelSerializer):
    """
    Serializer for Grade model.
    
    Handles grade recording with automatic calculation.
    """
    
    registration = CourseRegistrationSerializer(read_only=True)
    registration_id = serializers.IntegerField(write_only=True)
    letter_grade = serializers.CharField(read_only=True)
    grade_point = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id',
            'registration',
            'registration_id',
            'score',
            'letter_grade',
            'grade_point',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'letter_grade', 'grade_point']
    
    def validate_score(self, value: float) -> float:
        """
        Validate that score is between 0 and 100.
        
        Args:
            value: Score to validate
            
        Returns:
            Validated score
            
        Raises:
            ValidationError: If score is out of range
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError('Score must be between 0 and 100.')
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that grade doesn't already exist for this registration.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If grade already exists
        """
        registration_id = attrs.get('registration_id')
        
        queryset = Grade.objects.filter(registration_id=registration_id)
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'A grade already exists for this course registration.'
            )
        
        return attrs


class GradeDetailSerializer(GradeSerializer):
    """
    Detailed serializer for Grade with full nested information.
    """
    
    registration = CourseRegistrationDetailSerializer(read_only=True)
    
    class Meta(GradeSerializer.Meta):
        fields = GradeSerializer.Meta.fields


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model.
    
    Handles attendance tracking with nested relationships.
    """
    
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'student_id',
            'course',
            'course_id',
            'date',
            'status',
            'status_display',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status_display']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that attendance doesn't already exist for this date.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If attendance already exists
        """
        student_id = attrs.get('student_id')
        course_id = attrs.get('course_id')
        attendance_date = attrs.get('date')
        
        queryset = Attendance.objects.filter(
            student_id=student_id,
            course_id=course_id,
            date=attendance_date
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'Attendance record already exists for this student, course, and date.'
            )
        
        return attrs


class AttendanceDetailSerializer(AttendanceSerializer):
    """
    Detailed serializer for Attendance with full nested information.
    """
    
    student = StudentProfileDetailSerializer(read_only=True)
    
    class Meta(AttendanceSerializer.Meta):
        fields = AttendanceSerializer.Meta.fields


class FacultySerializer(serializers.ModelSerializer):
    """
    Serializer for Faculty model.
    """
    
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'code']
        read_only_fields = ['id']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model.
    """
    
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.IntegerField(write_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'faculty', 'faculty_id', 'faculty_name']
        read_only_fields = ['id']


class ProgrammeSerializer(serializers.ModelSerializer):
    """
    Serializer for Programme model.
    """
    
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)
    
    class Meta:
        model = Programme
        fields = ['id', 'name', 'code', 'department', 'department_id', 'department_name', 'faculty_name', 
                  'duration_years', 'total_credit_units']
        read_only_fields = ['id']


class CourseAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for CourseAssignment model.
    """
    
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_title = serializers.CharField(source='course.course_title', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    semester_name = serializers.CharField(source='semester.get_name_display', read_only=True)
    
    class Meta:
        model = CourseAssignment
        fields = ['id', 'course', 'course_code', 'course_title', 'lecturer', 'lecturer_name',
                  'session', 'session_name', 'semester', 'semester_name', 'role', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']


class TimetableSerializer(serializers.ModelSerializer):
    """
    Serializer for Timetable model.
    """
    
    course_code = serializers.CharField(source='course_assignment.course.course_code', read_only=True)
    course_title = serializers.CharField(source='course_assignment.course.course_title', read_only=True)
    lecturer_name = serializers.CharField(source='course_assignment.lecturer.get_full_name', read_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = Timetable
        fields = ['id', 'course_assignment', 'course_code', 'course_title', 'lecturer_name',
                  'day_of_week', 'day_of_week_display', 'start_time', 'end_time', 'venue',
                  'session', 'semester']
        read_only_fields = ['id']


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for Announcement model.
    """
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    target_audience_display = serializers.CharField(source='get_target_audience_display', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'target_audience', 'target_audience_display', 
                  'is_active', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResultSerializer(serializers.ModelSerializer):
    """
    Serializer for Result model.
    """
    
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.username', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_title = serializers.CharField(source='course.course_title', read_only=True)
    course_credit_unit = serializers.IntegerField(source='course.credit_unit', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    semester_name = serializers.CharField(source='semester.get_name_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    grade_point = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    quality_point = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Result
        fields = ['id', 'student', 'student_name', 'student_matric', 'course', 'course_code', 
                  'course_title', 'course_credit_unit', 'lecturer', 'lecturer_name', 'session', 'session_name', 
                  'semester', 'semester_name', 'ca_score', 'exam_score', 'total_score', 
                  'grade', 'grade_point', 'quality_point', 'status', 'status_display', 'remarks', 'submitted_at', 
                  'approved_at', 'approved_by']
        read_only_fields = ['id', 'total_score', 'grade', 'grade_point', 'quality_point', 'submitted_at', 'approved_at', 'approved_by']


class BatchResultSerializer(serializers.Serializer):
    """
    Serializer for batch result submission.
    """
    results = ResultSerializer(many=True)
    
    def create(self, validated_data):
        """Create multiple results in a single transaction."""
        from django.db import transaction
        from academics.models import Result, AcademicSession, Semester, ActivityLog
        
        results_data = validated_data['results']
        created_results = []
        
        # Get current active session and semester
        try:
            current_session = AcademicSession.objects.filter(is_active=True).first()
            current_semester = Semester.objects.filter(is_active=True).first()
        except:
            current_session = None
            current_semester = None
        
        # Get the lecturer from the first result (all should be from same lecturer)
        lecturer = None
        if results_data and results_data[0].get('lecturer'):
            from users.models import User
            lecturer = User.objects.get(id=results_data[0]['lecturer'])
        
        with transaction.atomic():
            for result_data in results_data:
                result = Result.objects.create(
                    student=result_data['student'],
                    course=result_data['course'],
                    lecturer=result_data.get('lecturer'),
                    session=current_session,
                    semester=current_semester,
                    ca_score=result_data.get('ca_score', 0),
                    exam_score=result_data.get('exam_score', 0),
                    status='pending'
                )
                created_results.append(result)
            
            # Log activity for the lecturer
            if lecturer and created_results:
                ActivityLog.objects.create(
                    user=lecturer,
                    action='SUBMIT_RESULTS',
                    entity_type='Result',
                    entity_id=created_results[0].id,
                    description=f'Submitted {len(created_results)} results for {created_results[0].course.course_code}'
                )
        
        return {'results': created_results}


class ActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for ActivityLog model.
    """
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_name', 'user_role', 'action', 'entity_type', 
                  'entity_id', 'description', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class CGPARecordSerializer(serializers.ModelSerializer):
    """
    Serializer for CGPARecord model.
    """
    
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.username', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    semester_name = serializers.CharField(source='semester.get_name_display', read_only=True)
    
    class Meta:
        model = CGPARecord
        fields = ['id', 'student', 'student_name', 'student_matric', 'session', 'session_name',
                  'semester', 'semester_name', 'cgpa', 'total_credit_units', 
                  'total_quality_points', 'calculated_at']
        read_only_fields = ['id', 'calculated_at']
