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
from django.db import models, transaction
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
    programme_name = serializers.CharField(source='programme.name', read_only=True)
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
            'programme_name',
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
            # Generate student_id first if not provided
            if not validated_data.get('student_id'):
                # Get faculty code from programme
                faculty_code = 'NS'  # Default
                if programme:
                    if programme.department and programme.department.faculty:
                        faculty_code = programme.department.faculty.code
                    logger.info(f"Faculty code: {faculty_code} from programme {programme.name}")
                else:
                    logger.warning("No programme provided, using default faculty code 'NS'")
                
                # Get serial number for this faculty/year using SerialNumber model
                from users.models import StudentProfile, SerialNumber
                year = datetime.now().year
                try:
                    # Get the highest allocated serial for this year/faculty/type
                    max_serial = SerialNumber.objects.filter(
                        serial_type='student',
                        year=year,
                        faculty_code=faculty_code
                    ).aggregate(models.Max('serial_number'))['serial_number__max'] or 0
                    
                    # Allocate the next serial number
                    next_serial = max_serial + 1
                    
                    # Record this serial allocation
                    SerialNumber.objects.create(
                        serial_type='student',
                        year=year,
                        faculty_code=faculty_code,
                        serial_number=next_serial
                    )
                    
                    serial = str(next_serial).zfill(3)
                    validated_data['student_id'] = f"{year}/{faculty_code}/{serial}"
                    logger.info(f"Generated student_id: {validated_data['student_id']}")
                except Exception as e:
                    logger.error(f"Error generating student_id: {e}", exc_info=True)
                    raise serializers.ValidationError(f"Failed to generate student ID: {str(e)}")
            
            # Generate username as year + faculty_code + serial + @school.edu (all lowercase)
            student_id = validated_data.get('student_id', '')
            if student_id:
                # Remove slashes from student_id and convert to lowercase
                username = student_id.replace('/', '').lower() + '@school.edu'
            else:
                # Fallback to name-based username if no student_id
                username = f"{user_data['last_name'].lower()}{user_data['first_name'].lower()}@school.edu"
            
            # Check if username already exists and generate a new one if needed
            from users.models import User
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                if student_id:
                    # Increment serial number if using student_id
                    parts = student_id.split('/')
                    if len(parts) == 3:
                        year, faculty, serial = parts
                        new_serial = str(int(serial) + counter).zfill(3)
                        new_student_id = f"{year}/{faculty}/{new_serial}"
                        username = new_student_id.replace('/', '').lower() + '@school.edu'
                else:
                    # Add number if using name-based username
                    username = f"{original_username.split('@')[0]}{counter}@school.edu"
                counter += 1
                logger.warning(f"Username {username} already exists, generating new one")
            
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
        
        # Create student profile with user and programme
        if user:
            validated_data['user'] = user
        if programme:
            validated_data['programme'] = programme
        try:
            student_profile = super().create(validated_data)
            
            # Auto-assign courses based on entry level
            grade_level = validated_data.get('grade_level')
            logger.info(f"Grade level from validated_data: {grade_level}")
            if grade_level:
                logger.info(f"Auto-assigning courses for level: {grade_level}")
                try:
                    from academics.models import Level, Course, CourseRegistration, AcademicSession, Semester
                    
                    # Try multiple level name formats
                    level_name_variants = [
                        f"{grade_level} Level",
                        str(grade_level),
                        f"{grade_level}L",
                        f"L{grade_level}"
                    ]
                    
                    level = None
                    for level_name in level_name_variants:
                        logger.info(f"Trying to find level with name: {level_name}")
                        level = Level.objects.filter(name__iexact=level_name).first()
                        if level:
                            logger.info(f"Found level: {level.name} (ID: {level.id})")
                            break
                    
                    if not level:
                        # Try to find level by name containing the grade level number
                        level = Level.objects.filter(name__icontains=str(grade_level)).first()
                        if level:
                            logger.info(f"Found level by partial match: {level.name} (ID: {level.id})")
                    
                    if level:
                        # Get current academic session
                        current_session = AcademicSession.objects.filter(is_current=True).first()
                        if not current_session:
                            logger.warning("No current academic session found, using first available session")
                            current_session = AcademicSession.objects.first()
                        
                        if current_session:
                            logger.info(f"Using session: {current_session.name} (ID: {current_session.id})")
                            
                            # Get all courses for this level (include inactive courses if no active ones)
                            courses = Course.objects.filter(level=level)
                            active_courses = courses.filter(is_active=True)
                            logger.info(f"Found {active_courses.count()} active courses for level {level.name}")
                            
                            if active_courses.count() == 0:
                                logger.warning(f"No active courses found for level {level.name}, trying all courses")
                                courses_to_assign = courses
                            else:
                                courses_to_assign = active_courses
                            
                            logger.info(f"Assigning {courses_to_assign.count()} courses")
                            
                            # Register student for all courses in both semesters
                            semesters = Semester.objects.all()
                            logger.info(f"Found {semesters.count()} semesters")
                            
                            assigned_count = 0
                            for semester in semesters:
                                semester_courses = courses_to_assign.filter(semester=semester)
                                logger.info(f"Found {semester_courses.count()} courses for {semester.name}")
                                
                                for course in semester_courses:
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
                                        assigned_count += 1
                                        logger.info(f"Registered {student_profile.student_id} for course {course.course_code} ({semester.name})")
                                    else:
                                        logger.info(f"Already registered for {course.course_code} ({semester.name})")
                            
                            logger.info(f"Total courses assigned: {assigned_count}")
                        else:
                            logger.warning("No academic session available for course registration")
                    else:
                        logger.warning(f"Level for grade {grade_level} not found in database")
                        # List all available levels for debugging
                        all_levels = Level.objects.all()
                        logger.info(f"Available levels in database: {list(all_levels.values_list('name', flat=True))}")
                except Exception as e:
                    logger.error(f"Error auto-assigning courses: {e}", exc_info=True)
                    # Don't fail student creation if course assignment fails
            else:
                logger.warning("No grade_level provided - skipping course assignment")
            
            # Register parent if parent data is provided
            logger.info(f"Parent data check - first_name: {parent_first_name}, last_name: {parent_last_name}, email: {parent_email}")
            if parent_first_name and parent_last_name and parent_email:
                logger.info(f"Registering parent: {parent_first_name} {parent_last_name}")
                
                try:
                    # Check if parent with this email already exists
                    from users.models import ParentProfile, ParentStudentRelation
                    existing_parent_user = User.objects.filter(email=parent_email, role='parent').first()
                    
                    if existing_parent_user:
                        # Link to existing parent
                        logger.info(f"Found existing parent with email {parent_email}, linking to existing parent")
                        parent_profile = existing_parent_user.parent_profile
                        # Update parent info if needed
                        existing_parent_user.first_name = parent_first_name
                        existing_parent_user.last_name = parent_last_name
                        if parent_phone:
                            existing_parent_user.phone = parent_phone
                        existing_parent_user.save()
                        if parent_phone:
                            parent_profile.phone_number = parent_phone
                            parent_profile.save()
                    else:
                        # Create new parent
                        logger.info(f"Creating new parent account for {parent_email}")
                        # Create parent username by adding plasu. prefix to their email
                        parent_username = f"plasu.{parent_email}"
                        
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
                        parent_profile = ParentProfile.objects.create(
                            user=parent_user,
                            phone_number=parent_phone or ''
                        )
                        
                        # Send registration email to parent (only for new parents)
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
                    
                    # Check if this parent-student relationship already exists
                    existing_relation = ParentStudentRelation.objects.filter(
                        parent=parent_profile,
                        student=student_profile
                    ).first()
                    
                    if not existing_relation:
                        # Link parent to student
                        ParentStudentRelation.objects.create(
                            parent=parent_profile,
                            student=student_profile,
                            relationship_type=parent_relationship or 'guardian'
                        )
                        logger.info(f"Parent linked to student: {student_profile.student_id}")
                    else:
                        logger.info(f"Parent already linked to student: {student_profile.student_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to create/link parent account: {e}", exc_info=True)
                    # Don't fail student creation if parent creation fails
            else:
                logger.info("No parent data provided or incomplete - skipping parent registration")
            
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
    children_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ParentProfile
        fields = [
            'id',
            'user',
            'user_id',
            'user_data',
            'occupation',
            'phone_number',
            'children_count'
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
            # Create parent username by adding plasu. prefix to their email
            parent_email = user_data.get('email', '')
            username = f"plasu.{parent_email}"
            logger.info(f"Creating user with username: {username}, email: {parent_email}")
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
    parent_children_count = serializers.IntegerField(read_only=True)
    student = StudentProfileSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ParentStudentRelation
        fields = [
            'id',
            'parent',
            'parent_id',
            'parent_children_count',
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
    parent_children_count = serializers.IntegerField(read_only=True)
    student = StudentProfileDetailSerializer(read_only=True)
    
    class Meta(ParentStudentRelationSerializer.Meta):
        fields = ParentStudentRelationSerializer.Meta.fields


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user information.
    
    Adds user role and profile information to the token response.
    Uses username as the USERNAME_FIELD (school email).
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Since USERNAME_FIELD is 'username', the default field is already correct
        # No need to modify fields
    
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
        
        Args:
            attrs: Attributes to validate
            
        Returns:
            Dictionary with token and user information
        """
        # Use default validation since USERNAME_FIELD is 'username'
        data = super().validate(attrs)
        
        # Add user information to response
        user = self.user
        
        # Get profile information based on role
        profile_data = {}
        if user.role == 'student':
            try:
                if hasattr(user, 'studentprofile'):
                    profile = user.studentprofile
                    profile_data = {
                        'student_id': profile.student_id,
                        'grade_level': profile.grade_level,
                        'programme': profile.programme.name if profile.programme else None,
                    }
            except (StudentProfile.DoesNotExist, AttributeError):
                pass
        elif user.role == 'lecturer':
            try:
                if hasattr(user, 'lecturerprofile'):
                    profile = user.lecturerprofile
                    profile_data = {
                        'staff_id': profile.staff_id,
                        'rank': profile.rank,
                        'department': profile.department.name if profile.department else None,
                    }
            except (LecturerProfile.DoesNotExist, AttributeError):
                pass
        elif user.role == 'parent':
            try:
                if hasattr(user, 'parentprofile'):
                    profile = user.parentprofile
                    profile_data = {
                        'phone': profile.phone,
                        'address': profile.address,
                    }
            except (ParentProfile.DoesNotExist, AttributeError):
                pass
        
        # Add user and profile data to response
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            **profile_data
        }
        
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
    courses = serializers.SerializerMethodField()
    courses_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = LecturerProfile
        fields = [
            'id', 'user', 'user_id', 'user_data', 'staff_id', 'rank', 'rank_display', 
            'employment_type', 'employment_type_display', 'department', 'department_name', 
            'faculty_name', 'date_of_birth', 'date_of_employment', 'username', 'email', 
            'first_name', 'last_name', 'courses', 'courses_ids'
        ]
        read_only_fields = ['id', 'date_of_employment', 'courses']
        extra_kwargs = {
            'user': {'required': False}
        }
    
    def get_courses(self, obj):
        """
        Get courses assigned to this lecturer.
        
        Args:
            obj: LecturerProfile instance
            
        Returns:
            List of courses assigned to this lecturer
        """
        from academics.models import CourseAssignment
        from academics.serializers import CourseSerializer
        
        try:
            # Get course assignments for this lecturer's user
            assignments = CourseAssignment.objects.filter(
                lecturer=obj.user
            ).select_related('course', 'session', 'semester')
            
            # Return course details from assignments
            courses = []
            for assignment in assignments:
                course_data = CourseSerializer(assignment.course).data
                course_data['session'] = assignment.session.name if assignment.session else None
                course_data['semester'] = assignment.semester.get_name_display() if assignment.semester else None
                course_data['role'] = assignment.role
                courses.append(course_data)
            
            return courses
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching courses for lecturer {obj.id}: {e}", exc_info=True)
            return []
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create lecturer profile with associated user and course assignments.
        
        Args:
            validated_data: Validated data from serializer
            
        Returns:
            Created LecturerProfile instance
        """
        import logging
        logger = logging.getLogger(__name__)
        
        user_data = validated_data.pop('user_data', None)
        user_id = validated_data.pop('user_id', None)
        courses_data = validated_data.pop('courses_ids', None)
        
        user = None
        if user_data:
            # Get faculty code from department
            department = validated_data.get('department')
            faculty_code = 'NS'  # Default
            if department and department.faculty:
                faculty_code = department.faculty.code.lower()
                logger.info(f"Faculty code: {faculty_code} from department {department.name}")
            else:
                logger.warning("No department provided, using default faculty code 'ns'")
            
            # Generate serial number for lecturers using SerialNumber model
            from users.models import LecturerProfile, User, SerialNumber
            try:
                # Get the highest allocated serial for this faculty/type
                year = datetime.now().year
                max_serial = SerialNumber.objects.filter(
                    serial_type='lecturer',
                    year=year,
                    faculty_code=faculty_code
                ).aggregate(models.Max('serial_number'))['serial_number__max'] or 0
                
                # Allocate the next serial number
                next_serial = max_serial + 1
                
                # Record this serial allocation
                SerialNumber.objects.create(
                    serial_type='lecturer',
                    year=year,
                    faculty_code=faculty_code,
                    serial_number=next_serial
                )
                
                serial = str(next_serial).zfill(4)
                logger.info(f"Generated lecturer serial: {serial} (max existing: {max_serial})")
            except Exception as e:
                logger.error(f"Error generating lecturer serial: {e}", exc_info=True)
                serial = '0001'
            
            # Generate username as plasu+serial+faculty_code+@school.edu (all lowercase)
            username = f"plasu{serial}{faculty_code}@school.edu"
            
            # Check if username already exists and generate a new one if needed
            counter = 1
            while User.objects.filter(username=username).exists():
                serial = str(int(serial) + counter).zfill(4)
                username = f"plasu{serial}{faculty_code}@school.edu"
                counter += 1
                logger.warning(f"Username {username} already exists, generating new one")
            
            logger.info(f"Creating lecturer user with username: {username}, email: {user_data.get('email')}")
            
            try:
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
                logger.info(f"Lecturer user created with ID: {user.id}")
            except Exception as e:
                logger.error(f"Error creating lecturer user: {e}", exc_info=True)
                raise serializers.ValidationError(f"Failed to create lecturer user: {str(e)}")
        elif user_id:
            user = User.objects.get(id=user_id)
        
        # Generate staff_id if not provided
        if not validated_data.get('staff_id'):
            validated_data['staff_id'] = f"PLASU/{datetime.now().year}/{uuid.uuid4().hex[:6].upper()}"
        
        # Create lecturer profile with user
        if user:
            validated_data['user'] = user
        lecturer = super().create(validated_data)
        
        # Create course assignments if courses were provided
        if courses_data and user:
            from academics.models import CourseAssignment, AcademicSession, Semester
            from academics.models import Course
            
            # Get current active session and semester (or default)
            try:
                current_session = AcademicSession.objects.filter(is_active=True).first()
                if not current_session:
                    current_session = AcademicSession.objects.first()
                
                # Get first semester from the current session
                current_semester = None
                if current_session:
                    current_semester = current_session.semesters.first()
                
                logger.info(f"Creating course assignments for lecturer {lecturer.id} with {len(courses_data)} courses")
                logger.info(f"Using session: {current_session.name if current_session else 'None'}")
                logger.info(f"Using semester: {current_semester.get_name_display() if current_semester else 'None'}")
                
                for course_id in courses_data:
                    try:
                        course = Course.objects.get(id=course_id)
                        assignment_data = {
                            'course': course,
                            'lecturer': user,
                            'role': 'primary'
                        }
                        if current_session:
                            assignment_data['session'] = current_session
                        if current_semester:
                            assignment_data['semester'] = current_semester
                            
                        CourseAssignment.objects.create(**assignment_data)
                        logger.info(f"Created course assignment for course {course.course_code}")
                    except Course.DoesNotExist:
                        logger.warning(f"Course with ID {course_id} not found, skipping assignment")
                    except Exception as e:
                        logger.error(f"Error creating course assignment for course {course_id}: {e}", exc_info=True)
                        
            except Exception as e:
                logger.error(f"Error setting up course assignments: {e}", exc_info=True)
        
        return lecturer


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
        assignments = CourseAssignment.objects.filter(lecturer=obj.user).select_related('course', 'session', 'semester')
        
        # Extract unique courses with session and semester info
        courses = []
        seen_courses = set()
        for assignment in assignments:
            if assignment.course.id not in seen_courses:
                seen_courses.add(assignment.course.id)
                course_data = CourseSerializer(assignment.course).data
                # Add session_id and semester_id from the assignment
                course_data['session_id'] = assignment.session.id if assignment.session else None
                course_data['semester_id'] = assignment.semester.id if assignment.semester else None
                courses.append(course_data)
        
        return courses
