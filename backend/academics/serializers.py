"""
Serializers for academic models.

This module provides serializers for all academic models including
sessions, semesters, levels, courses, enrollments, registrations,
grades, and attendance with proper validation and nested relationships.
"""

from datetime import date
from typing import Dict, Any, Optional
from django.utils import timezone

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
    department = serializers.SerializerMethodField(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Add backward compatibility fields
    code = serializers.CharField(source='course_code', read_only=True)
    title = serializers.CharField(source='course_title', read_only=True)
    
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
            'department',
            'department_id',
            'is_active',
            'code',
            'title'
        ]
        read_only_fields = ['id']
    
    def get_department(self, obj):
        if obj.department:
            return {
                'id': obj.department.id,
                'name': obj.department.name,
                'code': obj.department.code
            }
        return None
    
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
    
    def validate_department_id(self, value):
        """
        Validate department exists if provided.
        
        Args:
            value: Department ID to validate
            
        Returns:
            Validated department ID
            
        Raises:
            ValidationError: If department not found
        """
        if value is not None:
            try:
                Department.objects.get(pk=value)
            except Department.DoesNotExist:
                raise serializers.ValidationError('Department not found.')
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
        read_only_fields = ['id', 'registration_date']
    
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
    Detailed serializer for CourseRegistration with additional course information.
    """
    
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_title = serializers.CharField(source='course.course_title', read_only=True)
    credit_unit = serializers.IntegerField(source='course.credit_unit', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.student_id', read_only=True)
    
    class Meta(CourseRegistrationSerializer.Meta):
        fields = CourseRegistrationSerializer.Meta.fields + [
            'course_code',
            'course_title',
            'credit_unit',
            'student_name',
            'student_matric'
        ]


class GradeSerializer(serializers.ModelSerializer):
    """
    Serializer for Grade model.
    
    Handles grade assignments with validation.
    """
    
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    session = AcademicSessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True)
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.IntegerField(write_only=True)
    grade_display = serializers.CharField(source='get_grade_display', read_only=True)
    
    class Meta:
        model = Grade
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
            'grade',
            'grade_display',
            'grade_point',
            'score',
            'graded_at'
        ]
        read_only_fields = ['id', 'graded_at']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that grade doesn't already exist.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If grade already exists
        """
        student_id = attrs.get('student_id')
        course_id = attrs.get('course_id')
        session_id = attrs.get('session_id')
        semester_id = attrs.get('semester_id')
        
        queryset = Grade.objects.filter(
            student_id=student_id,
            course_id=course_id,
            session_id=session_id,
            semester_id=semester_id
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'Grade already exists for this student/course in this session/semester.'
            )
        
        return attrs


class GradeDetailSerializer(GradeSerializer):
    """
    Detailed serializer for Grade with additional information.
    """
    
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_title = serializers.CharField(source='course.course_title', read_only=True)
    credit_unit = serializers.IntegerField(source='course.credit_unit', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.student_id', read_only=True)
    quality_point = serializers.IntegerField(read_only=True)
    
    class Meta(GradeSerializer.Meta):
        fields = GradeSerializer.Meta.fields + [
            'course_code',
            'course_title',
            'credit_unit',
            'student_name',
            'student_matric',
            'quality_point'
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model.
    
    Handles attendance tracking with validation.
    """
    
    student = serializers.SerializerMethodField()
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
            'remarks',
            'recorded_by',
            'recorded_at',
            'created_at'
        ]
        read_only_fields = ['id', 'recorded_by', 'recorded_at', 'created_at']
    
    def get_student(self, obj):
        """Get student profile from user."""
        try:
            from users.models import StudentProfile
            # Handle case where obj.student might be a string (corrupted data)
            if isinstance(obj.student, str):
                # Try to find student by ID or username
                try:
                    # If it's a string representation, try to extract the username
                    import re
                    match = re.match(r'(\w+)', obj.student)
                    if match:
                        username = match.group(1)
                        student_profile = StudentProfile.objects.filter(user__username=username).first()
                        if student_profile:
                            return StudentProfileSerializer(student_profile).data
                except:
                    pass
                # Fallback for corrupted data
                return {
                    'id': None,
                    'username': obj.student,
                    'first_name': '',
                    'last_name': ''
                }
            
            # Normal case: obj.student is a User instance
            student_profile = StudentProfile.objects.get(user=obj.student)
            return StudentProfileSerializer(student_profile).data
        except StudentProfile.DoesNotExist:
            # Fallback to user data if no profile exists
            if hasattr(obj.student, 'id'):
                return {
                    'id': obj.student.id,
                    'username': obj.student.username,
                    'first_name': obj.student.first_name,
                    'last_name': obj.student.last_name
                }
            else:
                return {
                    'id': None,
                    'username': str(obj.student),
                    'first_name': '',
                    'last_name': ''
                }
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that attendance doesn't already exist for the same date.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If attendance already exists
        """
        student_profile_id = attrs.get('student_id')
        course_id = attrs.get('course_id')
        date = attrs.get('date')
        
        # Convert student_profile_id to user_id for the query
        try:
            from users.models import StudentProfile
            student_profile = StudentProfile.objects.get(id=student_profile_id)
            user_id = student_profile.user_id
        except StudentProfile.DoesNotExist:
            raise serializers.ValidationError('Student profile not found')
        
        queryset = Attendance.objects.filter(
            student_id=user_id,
            course_id=course_id,
            date=date
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'Attendance already marked for this student/course on this date.'
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create attendance record with proper student ID conversion."""
        student_profile_id = validated_data.pop('student_id')
        
        # Convert student_profile_id to user_id
        try:
            from users.models import StudentProfile
            student_profile = StudentProfile.objects.get(id=student_profile_id)
            validated_data['student'] = student_profile.user
        except StudentProfile.DoesNotExist:
            raise serializers.ValidationError('Student profile not found')
        
        return super().create(validated_data)
    
    def create(self, validated_data):
        """Create attendance record with proper student ID conversion."""
        student_profile_id = validated_data.pop('student_id')
        
        # Convert student_profile_id to user_id
        try:
            from users.models import StudentProfile
            student_profile = StudentProfile.objects.get(id=student_profile_id)
            validated_data['student'] = student_profile.user
        except StudentProfile.DoesNotExist:
            raise serializers.ValidationError('Student profile not found')
        
        return super().create(validated_data)


class AttendanceDetailSerializer(AttendanceSerializer):
    """
    Detailed serializer for Attendance with additional information.
    """
    
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_title = serializers.CharField(source='course.course_title', read_only=True)
    student_name = serializers.SerializerMethodField()
    student_matric = serializers.SerializerMethodField()
    
    class Meta(AttendanceSerializer.Meta):
        fields = AttendanceSerializer.Meta.fields + [
            'course_code',
            'course_title',
            'student_name',
            'student_matric'
        ]
    
    def get_student_name(self, obj):
        """Get student full name."""
        return f"{obj.student.first_name} {obj.student.last_name}".strip()
    
    def get_student_matric(self, obj):
        """Get student matric number."""
        try:
            from users.models import StudentProfile
            student_profile = StudentProfile.objects.get(user=obj.student)
            return student_profile.student_id
        except StudentProfile.DoesNotExist:
            return None


class FacultySerializer(serializers.ModelSerializer):
    """
    Serializer for Faculty model.
    
    Handles faculty management with validation.
    """
    
    class Meta:
        model = Faculty
        fields = [
            'id',
            'name',
            'code'
        ]
        read_only_fields = ['id']
    
    def validate_code(self, value: str) -> str:
        """
        Validate faculty code uniqueness.
        
        Args:
            value: Faculty code to validate
            
        Returns:
            Validated faculty code
            
        Raises:
            ValidationError: If faculty code already exists
        """
        queryset = Faculty.objects.filter(code=value)
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError('A faculty with this code already exists.')
        
        return value


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model.
    
    Handles department management with nested faculty information.
    """
    
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.IntegerField(write_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'faculty',
            'faculty_id',
            'faculty_name'
        ]
        read_only_fields = ['id', 'faculty_name']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate department uniqueness within faculty.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If department name already exists in faculty
        """
        name = attrs.get('name')
        faculty_id = attrs.get('faculty_id')
        
        if name and faculty_id:
            queryset = Department.objects.filter(
                name=name,
                faculty_id=faculty_id
            )
            
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    'A department with this name already exists in this faculty.'
                )
        
        return attrs
    
    def validate_code(self, value: str) -> str:
        """
        Validate department code uniqueness.
        
        Args:
            value: Department code to validate
            
        Returns:
            Validated department code
            
        Raises:
            ValidationError: If department code already exists
        """
        queryset = Department.objects.filter(code=value)
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError('A department with this code already exists.')
        
        return value


class ProgrammeSerializer(serializers.ModelSerializer):
    """
    Serializer for Programme model.
    
    Handles programme management with nested department information.
    """
    
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Programme
        fields = [
            'id',
            'name',
            'code',
            'department',
            'department_id',
            'faculty_name',
            'department_name',
            'duration_years',
            'total_credit_units'
        ]
        read_only_fields = ['id', 'faculty_name', 'department_name']
    
    def validate_code(self, value: str) -> str:
        """
        Validate programme code uniqueness.
        
        Args:
            value: Programme code to validate
            
        Returns:
            Validated programme code
            
        Raises:
            ValidationError: If programme code already exists
        """
        queryset = Programme.objects.filter(code=value)
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError('A programme with this code already exists.')
        
        return value


class CourseAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for CourseAssignment model.
    
    Handles lecturer-course assignments with nested relationships.
    """
    
    lecturer = serializers.SerializerMethodField(read_only=True)
    lecturer_id = serializers.IntegerField(write_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    session = AcademicSessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True)
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CourseAssignment
        fields = [
            'id',
            'lecturer',
            'lecturer_id',
            'course',
            'course_id',
            'session',
            'session_id',
            'semester',
            'semester_id',
            'assigned_at'
        ]
        read_only_fields = ['id', 'assigned_at']
    
    def get_lecturer(self, obj):
        from users.serializers import LecturerProfileSerializer
        return LecturerProfileSerializer(obj.lecturer).data
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that assignment doesn't already exist.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If assignment already exists
        """
        lecturer_id = attrs.get('lecturer_id')
        course_id = attrs.get('course_id')
        session_id = attrs.get('session_id')
        semester_id = attrs.get('semester_id')
        
        queryset = CourseAssignment.objects.filter(
            lecturer_id=lecturer_id,
            course_id=course_id,
            session_id=session_id,
            semester_id=semester_id
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'This lecturer is already assigned to this course in this session/semester.'
            )
        
        return attrs


class TimetableSerializer(serializers.ModelSerializer):
    """
    Serializer for Timetable model.
    
    Handles timetable management with nested relationships.
    """
    
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    lecturer = serializers.SerializerMethodField(read_only=True)
    lecturer_id = serializers.IntegerField(write_only=True)
    session = AcademicSessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True)
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.IntegerField(write_only=True)
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    
    class Meta:
        model = Timetable
        fields = [
            'id',
            'course',
            'course_id',
            'lecturer',
            'lecturer_id',
            'session',
            'session_id',
            'semester',
            'semester_id',
            'day',
            'day_display',
            'start_time',
            'end_time',
            'venue',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_lecturer(self, obj):
        from users.serializers import LecturerProfileSerializer
        return LecturerProfileSerializer(obj.lecturer).data
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that there are no scheduling conflicts.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If there's a scheduling conflict
        """
        day = attrs.get('day')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        venue = attrs.get('venue')
        session_id = attrs.get('session_id')
        semester_id = attrs.get('semester_id')
        
        # Check for venue conflicts
        if day and start_time and end_time and venue:
            queryset = Timetable.objects.filter(
                day=day,
                venue=venue,
                session_id=session_id,
                semester_id=semester_id
            ).filter(
                models.Q(start_time__lt=end_time, end_time__gt=start_time)
            )
            
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    'There is a scheduling conflict for this venue at this time.'
                )
        
        return attrs


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for Announcement model.
    
    Handles announcement management with nested relationships.
    """
    
    author = serializers.SerializerMethodField(read_only=True)
    target_audience_display = serializers.CharField(
        source='get_target_audience_display',
        read_only=True
    )
    
    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'content',
            'author',
            'target_audience',
            'target_audience_display',
            'priority',
            'is_active',
            'published_at',
            'expires_at'
        ]
        read_only_fields = ['id', 'published_at']
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'first_name': obj.author.first_name,
            'last_name': obj.author.last_name
        }


class ResultSerializer(serializers.ModelSerializer):
    """
    Serializer for Result model.
    
    Handles student results with nested relationships.
    """
    
    student = serializers.SerializerMethodField()
    student_id = serializers.IntegerField(write_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    session = AcademicSessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True)
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Result
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
            'ca_score',
            'exam_score',
            'total_score',
            'grade',
            'status',
            'remarks',
            'submitted_at',
            'approved_at',
            'approved_by'
        ]
        read_only_fields = ['id', 'submitted_at', 'approved_at', 'approved_by']
    
    def get_student(self, obj):
        """Get student profile from user."""
        try:
            from users.models import StudentProfile
            # Handle case where obj.student might be a string (corrupted data)
            if isinstance(obj.student, str):
                # Try to find student by ID or username
                try:
                    # If it's a string representation, try to extract the username
                    import re
                    match = re.match(r'(\w+)', obj.student)
                    if match:
                        username = match.group(1)
                        student_profile = StudentProfile.objects.filter(user__username=username).first()
                        if student_profile:
                            return StudentProfileSerializer(student_profile).data
                except:
                    pass
                # Fallback for corrupted data
                return {
                    'id': None,
                    'username': obj.student,
                    'first_name': '',
                    'last_name': ''
                }
            
            # Normal case: obj.student is a User instance
            student_profile = StudentProfile.objects.get(user=obj.student)
            return StudentProfileSerializer(student_profile).data
        except StudentProfile.DoesNotExist:
            # Fallback to user data if no profile exists
            if hasattr(obj.student, 'id'):
                return {
                    'id': obj.student.id,
                    'username': obj.student.username,
                    'first_name': obj.student.first_name,
                    'last_name': obj.student.last_name
                }
            else:
                return {
                    'id': None,
                    'username': str(obj.student),
                    'first_name': '',
                    'last_name': ''
                }
    
    def create(self, validated_data):
        """Create result record with proper student ID conversion."""
        student_profile_id = validated_data.pop('student_id')
        
        # Convert student_profile_id to user_id
        try:
            from users.models import StudentProfile
            student_profile = StudentProfile.objects.get(id=student_profile_id)
            validated_data['student'] = student_profile.user
        except StudentProfile.DoesNotExist:
            raise serializers.ValidationError('Student profile not found')
        
        return super().create(validated_data)


class BatchResultSerializer(serializers.Serializer):
    """
    Serializer for batch result processing.
    
    Handles multiple result submissions in a single request.
    """
    
    course_id = serializers.IntegerField()
    action = serializers.CharField(required=False, default='submit')
    results = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_course_id(self, value):
        """Validate that the course exists."""
        try:
            Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError('Course not found')
        return value
    
    def validate(self, data):
        """Validate the entire payload."""
        if not data.get('results'):
            raise serializers.ValidationError('Results list is required')
        return data
    
    def create(self, validated_data):
        """
        Create or update multiple results in a single transaction.
        
        Args:
            validated_data: Validated data containing course_id, action, and results list
            
        Returns:
            Created/updated results
        """
        from django.db import transaction
        
        course_id = validated_data.pop('course_id')
        action = validated_data.pop('action', 'submit')
        results_data = validated_data.pop('results')
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise serializers.ValidationError('Course not found')
        
        # Get current active session and semester
        try:
            session = AcademicSession.objects.get(is_active=True)
            # Get the first semester (Semester model doesn't have is_active field)
            semester = Semester.objects.filter(session=session).first()
        except AcademicSession.DoesNotExist:
            raise serializers.ValidationError('No active session found')
        
        if not semester:
            raise serializers.ValidationError('No semester found for the active session')
        
        processed_results = []
        
        with transaction.atomic():
            for result_data in results_data:
                student_profile_id = result_data.get('student_id')
                ca_score = result_data.get('ca_score')
                exam_score = result_data.get('exam_score')
                
                if not student_profile_id:
                    continue
                
                # Get the StudentProfile and then the User
                try:
                    from users.models import StudentProfile
                    student_profile = StudentProfile.objects.get(id=student_profile_id)
                    student_user = student_profile.user
                except StudentProfile.DoesNotExist:
                    continue
                
                # For Result model, status is always 'pending' until approved
                # The distinction between draft and submitted is based on submitted_at
                status = 'pending'
                
                # Update or create result
                result, created = Result.objects.update_or_create(
                    student=student_user,
                    course=course,
                    session=session,
                    semester=semester,
                    defaults={
                        'ca_score': ca_score,
                        'exam_score': exam_score,
                        'status': status,
                        'lecturer': self.context['request'].user,
                        'submitted_at': timezone.now() if action == 'submit' else None,
                        'remarks': ''  # Clear remarks when re-submitting
                    }
                )
                
                processed_results.append(result)
        
        return {'results': processed_results, 'action': action}


class ActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for ActivityLog model.
    
    Handles activity logging with user information.
    """
    
    user = serializers.SerializerMethodField(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_name', 'user_role', 'action', 'entity_type', 
                  'entity_id', 'description', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }


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
