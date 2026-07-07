"""
Serializers for user models.

This module provides serializers for User, StudentProfile, ParentProfile,
and ParentStudentRelation models with proper validation and nested relationships.
"""

from datetime import date, datetime
from typing import Dict, Any, Optional
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import StudentProfile, ParentProfile, ParentStudentRelation, LecturerProfile
from academics.models import Programme

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Handles user creation and updates with password validation.
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Password for the user account'
    )
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'password',
            'is_active',
            'date_joined',
            'last_login'
        ]
        read_only_fields = ['id', 'is_active', 'date_joined', 'last_login']
        extra_kwargs = {
            'username': {'help_text': 'Unique username for the user'},
            'email': {'help_text': 'Email address of the user'},
            'role': {'help_text': 'Role of the user (student, parent, or admin)'}
        }
    
    def validate_password(self, value: str) -> str:
        """
        Validate password using Django's password validators.
        
        Args:
            value: Password string to validate
            
        Returns:
            Validated password string
            
        Raises:
            ValidationError: If password fails validation
        """
        validate_password(value)
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            validated_data: Validated user data
            
        Returns:
            Created User instance
        """
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Serializer for nested user creation without password.
    
    Used when creating a user as part of another object creation.
    """
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'other_name',
            'email',
            'phone'
        ]


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for User model with limited fields.
    
    Used for displaying user information without sensitive data.
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'role']


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for StudentProfile model.
    
    Includes nested user information and calculated fields.
    """
    
    user = UserPublicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    user_data = UserNestedSerializer(write_only=True, required=False)
    programme = serializers.PrimaryKeyRelatedField(queryset=Programme.objects.all(), required=True)
    programme_code = serializers.CharField(write_only=True, required=False, allow_null=True, help_text='Programme code (e.g., "CS-001")')
    age = serializers.SerializerMethodField()
    programme_display_name = serializers.CharField(source='programme.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    
    # Parent registration fields
    parent_first_name = serializers.CharField(write_only=True, required=False, allow_null=True)
    parent_last_name = serializers.CharField(write_only=True, required=False, allow_null=True)
    parent_email = serializers.EmailField(write_only=True, required=False, allow_null=True)
    parent_phone = serializers.CharField(write_only=True, required=False, allow_null=True)
    parent_relationship = serializers.ChoiceField(
        choices=['father', 'mother', 'guardian'],
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'user_id',
            'user_data',
            'student_id',
            'gender',
            'date_of_birth',
            'grade_level',
            'programme',
            'programme_code',
            'programme_display_name',
            'department_name',
            'faculty_name',
            'enrollment_date',
            'age',
            'parent_first_name',
            'parent_last_name',
            'parent_email',
            'parent_phone',
            'parent_relationship'
        ]
        read_only_fields = ['id', 'enrollment_date', 'age']
        extra_kwargs = {
            'user': {'required': False}
        }
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create student profile with associated user.
        
        Args:
            validated_data: Validated data from serializer
            
        Returns:
            Created StudentProfile instance
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info("StudentProfileSerializer.create called")
        logger.info(f"Validated data keys: {validated_data.keys()}")
        
        user_data = validated_data.pop('user_data', None)
        user_id = validated_data.pop('user_id', None)
        programme = validated_data.pop('programme', None)
        programme_code = validated_data.pop('programme_code', None)
        
        # Extract parent registration fields
        parent_first_name = validated_data.pop('parent_first_name', None)
        parent_last_name = validated_data.pop('parent_last_name', None)
        parent_email = validated_data.pop('parent_email', None)
        parent_phone = validated_data.pop('parent_phone', None)
        parent_relationship = validated_data.pop('parent_relationship', None)
        
        user = None
        if user_data:
            # Create user from nested data with new username format
            # Use matric number as username for uniqueness
            matric_number = validated_data.get('student_id', '')
            if matric_number:
                username = f"{matric_number}@school.edu"
            else:
                # Fallback to name-based username if no matric number yet
                username = f"{user_data['last_name'].lower()}{user_data['first_name'].lower()}@school.edu"
            logger.info(f"Creating user with username: {username}, email: {user_data.get('email')}")
            
            try:
                user = User.objects.create(
                    username=username,
                    email=user_data.get('email', ''),
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    phone=user_data.get('phone', ''),
                    other_name=user_data.get('other_name', ''),
                    role='student'
                )
                # Set default password
                default_password = 'school1234'
                user.set_password(default_password)
                user.save()
                logger.info(f"User created with ID: {user.id}, default password set")
            except Exception as e:
                logger.error(f"Error creating user: {e}", exc_info=True)
                raise serializers.ValidationError(f"Failed to create user: {str(e)}")
        elif user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise serializers.ValidationError("User with provided ID does not exist")
        
        # Programme is required - if not provided, raise error
        if not programme:
            raise serializers.ValidationError("Programme is required for student registration")
        
        logger.info(f"Programme: {programme.name} ({programme.code})")
        
        # Generate student_id with new format: year/faculty_code/serial
        if not validated_data.get('student_id'):
            # Get faculty code from programme
            faculty_code = 'NS'  # Default
            if programme:
                if programme.department and programme.department.faculty:
                    faculty_code = programme.department.faculty.code
                logger.info(f"Faculty code: {faculty_code} from programme {programme.name}")
            else:
                logger.warning("No programme provided, using default faculty code 'NS'")
            
            # Get serial number for this faculty/year
            from users.models import StudentProfile
            year = datetime.now().year
            try:
                count = StudentProfile.objects.filter(
                    student_id__startswith=f"{year}/{faculty_code}"
                ).count()
                serial = str(count + 1).zfill(3)
                validated_data['student_id'] = f"{year}/{faculty_code}/{serial}"
                logger.info(f"Generated student_id: {validated_data['student_id']}")
            except Exception as e:
                logger.error(f"Error generating student_id: {e}", exc_info=True)
                raise serializers.ValidationError(f"Failed to generate student ID: {str(e)}")
        
        # Create student profile with user and programme
        if user:
            validated_data['user'] = user
        if programme:
            validated_data['programme'] = programme
        try:
            student_profile = super().create(validated_data)
            
            # Auto-assign courses based on entry level
            grade_level = validated_data.get('grade_level')
            if grade_level:
                logger.info(f"Auto-assigning courses for level: {grade_level}")
                try:
                    from academics.models import Level, Course, CourseRegistration, AcademicSession, Semester
                    
                    # Find the level object (e.g., "100 Level" for grade_level 100)
                    level_name = f"{grade_level} Level"
                    level = Level.objects.filter(name=level_name).first()
                    
                    if level:
                        logger.info(f"Found level: {level.name}")
                        
                        # Get current academic session
                        current_session = AcademicSession.objects.filter(is_current=True).first()
                        if not current_session:
                            logger.warning("No current academic session found, using first available session")
                            current_session = AcademicSession.objects.first()
                        
                        if current_session:
                            logger.info(f"Using session: {current_session.name}")
                            
                            # Get all courses for this level
                            courses = Course.objects.filter(level=level, is_active=True)
                            logger.info(f"Found {courses.count()} courses for level {level.name}")
                            
                            # Register student for all courses in both semesters
                            semesters = Semester.objects.all()
                            for semester in semesters:
                                for course in courses.filter(semester=semester):
                                    # Check if already registered
                                    existing = CourseRegistration.objects.filter(
                                        student=student_profile,
                                        course=course,
                                        session=current_session,
                                        semester=semester
                                    ).exists()
                                    
                                    if not existing:
                                        CourseRegistration.objects.create(
                                            student=student_profile,
                                            course=course,
                                            session=current_session,
                                            semester=semester,
                                            is_carryover=False
                                        )
                                        logger.info(f"Registered {student_profile.student_id} for course {course.course_code} ({semester.name})")
                                    else:
                                        logger.info(f"Already registered for {course.course_code} ({semester.name})")
                        else:
                            logger.warning("No academic session available for course registration")
                    else:
                        logger.warning(f"Level '{level_name}' not found in database")
                except Exception as e:
                    logger.error(f"Error auto-assigning courses: {e}", exc_info=True)
                    # Don't fail student creation if course assignment fails
            
            # Register parent if parent data is provided
            if parent_first_name and parent_last_name and parent_email:
                logger.info(f"Registering parent: {parent_first_name} {parent_last_name}")
                
                # Create parent username based on student's matric number
                parent_username = f"{student_profile.student_id}_parent@school.edu"
                
                # Create parent user
                parent_user = User.objects.create(
                    username=parent_username,
                    email=parent_email,
                    first_name=parent_first_name,
                    last_name=parent_last_name,
                    phone=parent_phone or '',
                    role='parent'
                )
                parent_user.set_password('school1234')
                parent_user.save()
                
                # Create parent profile
                from users.models import ParentProfile
                parent_profile = ParentProfile.objects.create(
                    user=parent_user,
                    phone_number=parent_phone or ''
                )
                
                # Link parent to student
                from users.models import ParentStudentRelation
                ParentStudentRelation.objects.create(
                    parent=parent_profile,
                    student=student_profile,
                    relationship_type=parent_relationship or 'guardian'
                )
                
                logger.info(f"Parent registered and linked to student: {student_profile.student_id}")
                
                # Send registration email to parent
                from users.utils.email_utils import send_parent_registration_email
                try:
                    send_parent_registration_email(
                        email=parent_email,
                        first_name=parent_first_name,
                        last_name=parent_last_name,
                        password='school1234',
                        child_name=f"{user.first_name} {user.last_name}" if user else '',
                        child_matric=student_profile.student_id,
                        school_email=parent_username
                    )
                    logger.info(f"Parent registration email sent to: {parent_email}")
                except Exception as e:
                    logger.error(f"Failed to send parent registration email: {e}", exc_info=True)
            
            return student_profile
        except Exception as e:
            logger.error(f"Error creating student profile: {e}", exc_info=True)
            raise serializers.ValidationError(f"Failed to create student profile: {str(e)}")
    
    def get_age(self, obj: StudentProfile) -> Optional[int]:
        """
        Calculate student's age based on date of birth.
        
        Args:
            obj: StudentProfile instance
            
        Returns:
            Age in years, or None if date of birth not set
        """
        if obj.date_of_birth:
            today = date.today()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None
    
    def validate_student_id(self, value: str) -> str:
        """
        Validate student ID uniqueness.
        
        Args:
            value: Student ID to validate
            
        Returns:
            Validated student ID
            
        Raises:
            ValidationError: If student ID already exists
        """
        user_id = self.initial_data.get('user_id') if hasattr(self, 'initial_data') else None
        queryset = StudentProfile._default_manager.filter(student_id=value)
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError('A student with this student ID already exists.')
        
        return value


class StudentProfileDetailSerializer(StudentProfileSerializer):
    """
    Detailed serializer for StudentProfile with full user information.
    """
    
    user = UserSerializer(read_only=True)
    
    class Meta(StudentProfileSerializer.Meta):
        fields = StudentProfileSerializer.Meta.fields


class ParentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for ParentProfile model.
    
    Includes nested user information.
    """
    
    user = UserPublicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    user_data = UserNestedSerializer(write_only=True, required=False)
    
    class Meta:
        model = ParentProfile
        fields = [
            'id',
            'user',
            'user_id',
            'user_data',
            'occupation',
            'phone_number'
        ]
        read_only_fields = ['id']
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create parent profile with associated user.
        
        Args:
            validated_data: Validated data from serializer
            
        Returns:
            Created ParentProfile instance
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info("ParentProfileSerializer.create called")
        
        user_data = validated_data.pop('user_data', None)
        user_id = validated_data.pop('user_id', None)
        
        user = None
        if user_data:
            # Create user from nested data
            username = f"{user_data['last_name'].lower()}{user_data['first_name'].lower()}@school.edu"
            logger.info(f"Creating user with username: {username}, email: {user_data.get('email')}")
            user = User.objects.create(
                username=username,
                email=user_data.get('email', ''),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                phone=user_data.get('phone', ''),
                other_name=user_data.get('other_name', ''),
                role='parent'
            )
            # Set default password
            default_password = 'school1234'
            user.set_password(default_password)
            user.save()
            logger.info(f"User created with ID: {user.id}, default password set")
        elif user_id:
            user = User.objects.get(id=user_id)
        
        # Create parent profile with user
        if user:
            validated_data['user'] = user
        return super().create(validated_data)


class ParentProfileDetailSerializer(ParentProfileSerializer):
    """
    Detailed serializer for ParentProfile with full user information.
    """
    
    user = UserSerializer(read_only=True)
    
    class Meta(ParentProfileSerializer.Meta):
        fields = ParentProfileSerializer.Meta.fields


class ParentStudentRelationSerializer(serializers.ModelSerializer):
    """
    Serializer for ParentStudentRelation model.
    
    Handles parent-student relationships with proper validation.
    """
    
    parent = ParentProfileSerializer(read_only=True)
    parent_id = serializers.IntegerField(write_only=True)
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ParentStudentRelation
        fields = [
            'id',
            'parent',
            'parent_id',
            'student',
            'student_id',
            'relationship_type'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the relationship doesn't already exist.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If relationship already exists
        """
        parent_id = attrs.get('parent_id')
        student_id = attrs.get('student_id')
        
        queryset = ParentStudentRelation._default_manager.filter(
            parent_id=parent_id,
            student_id=student_id
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'A relationship between this parent and student already exists.'
            )
        
        return attrs


class ParentStudentRelationDetailSerializer(ParentStudentRelationSerializer):
    """
    Detailed serializer for ParentStudentRelation with full nested information.
    """
    
    parent = ParentProfileDetailSerializer(read_only=True)
    student = StudentProfileDetailSerializer(read_only=True)
    
    class Meta(ParentStudentRelationSerializer.Meta):
        fields = ParentStudentRelationSerializer.Meta.fields


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user information.
    
    Adds user role and profile information to the token response.
    Supports both username and email for login.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email field optional (will be set from username if provided)
        self.fields['email'].required = False
        # Add username field as an alternative to email (since USERNAME_FIELD = 'email')
        self.fields['username'] = serializers.CharField(required=False, write_only=True)
    
    @classmethod
    def get_token(cls, user: User) -> Any:
        """
        Add custom claims to the token.
        
        Args:
            user: User instance
            
        Returns:
            Token with custom claims
        """
        token = super().get_token(user)
        
        # Add custom claims
        token['role'] = user.role
        token['username'] = user.username
        
        return token
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and return token data with user information.
        
        Supports both username and email for login.
        
        Args:
            attrs: Attributes to validate
            
        Returns:
            Dictionary with token and user information
        """
        # If username is provided, use it to find the user and set email
        if 'username' in attrs and attrs['username']:
            username = attrs.pop('username')
            try:
                user = User.objects.get(username=username)
                attrs['email'] = user.email
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'detail': 'No active account found with the given username'
                })
        elif 'email' not in attrs or not attrs['email']:
            raise serializers.ValidationError({
                'detail': 'Either username or email is required'
            })
        
        data = super().validate(attrs)
        
        # Add user information to response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role
        }
        
        # Add profile information based on role
        if self.user.role == 'student' and hasattr(self.user, 'student_profile'):
            data['profile'] = StudentProfileSerializer(self.user.student_profile).data
        elif self.user.role == 'parent' and hasattr(self.user, 'parent_profile'):
            data['profile'] = ParentProfileSerializer(self.user.parent_profile).data
        elif self.user.role == 'lecturer' and hasattr(self.user, 'lecturer_profile'):
            data['profile'] = LecturerProfileSerializer(self.user.lecturer_profile).data
        
        return data


class LecturerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for LecturerProfile model.
    """
    
    user = UserPublicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    user_data = UserNestedSerializer(write_only=True, required=False)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    
    class Meta:
        model = LecturerProfile
        fields = [
            'id', 'user', 'user_id', 'user_data', 'staff_id', 'rank', 'rank_display', 
            'employment_type', 'employment_type_display', 'department', 'department_name', 
            'faculty_name', 'date_of_birth', 'date_of_employment', 'username', 'email', 
            'first_name', 'last_name'
        ]
        read_only_fields = ['id', 'date_of_employment']
        extra_kwargs = {
            'user': {'required': False}
        }
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create lecturer profile with associated user.
        
        Args:
            validated_data: Validated data from serializer
            
        Returns:
            Created LecturerProfile instance
        """
        user_data = validated_data.pop('user_data', None)
        user_id = validated_data.pop('user_id', None)
        
        user = None
        if user_data:
            # Create user from nested data
            username = f"{user_data['last_name'].lower()}{user_data['first_name'].lower()}@school.edu"
            user = User.objects.create(
                username=username,
                email=user_data.get('email', ''),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                phone=user_data.get('phone', ''),
                other_name=user_data.get('other_name', ''),
                role='lecturer'
            )
            # Set default password
            user.set_password('school1234')
            user.save()
        elif user_id:
            user = User.objects.get(id=user_id)
        
        # Generate staff_id if not provided
        if not validated_data.get('staff_id'):
            validated_data['staff_id'] = f"STF/{datetime.now().year}/{uuid.uuid4().hex[:6].upper()}"
        
        # Create lecturer profile with user
        if user:
            validated_data['user'] = user
        return super().create(validated_data)


class LecturerProfileDetailSerializer(LecturerProfileSerializer):
    """
    Detailed serializer for LecturerProfile with full nested information.
    """
    
    user = UserSerializer(read_only=True)
    department = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    
    class Meta(LecturerProfileSerializer.Meta):
        fields = LecturerProfileSerializer.Meta.fields + ['user', 'courses']
    
    def get_department(self, obj):
        from academics.serializers import DepartmentSerializer
        return DepartmentSerializer(obj.department).data
    
    def get_courses(self, obj):
        """Get courses assigned to this lecturer through CourseAssignment."""
        from academics.models import CourseAssignment
        from academics.serializers import CourseSerializer
        
        # Get all course assignments for this lecturer
        assignments = CourseAssignment.objects.filter(lecturer=obj.user).select_related('course')
        
        # Extract unique courses
        courses = []
        seen_courses = set()
        for assignment in assignments:
            if assignment.course.id not in seen_courses:
                seen_courses.add(assignment.course.id)
                course_data = CourseSerializer(assignment.course).data
                courses.append(course_data)
        
        return courses
