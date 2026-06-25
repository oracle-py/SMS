"""
Serializers for user models.

This module provides serializers for User, StudentProfile, ParentProfile,
and ParentStudentRelation models with proper validation and nested relationships.
"""

from datetime import date
from typing import Dict, Any, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import StudentProfile, ParentProfile, ParentStudentRelation

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
            validated_data: Validated data from serializer
            
        Returns:
            Created User instance
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """
        Update user instance with optional password update.
        
        Args:
            instance: User instance to update
            validated_data: Validated data from serializer
            
        Returns:
            Updated User instance
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


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
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'user_id',
            'student_id',
            'date_of_birth',
            'grade_level',
            'enrollment_date',
            'age'
        ]
        read_only_fields = ['id', 'enrollment_date', 'age']
    
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
    
    class Meta:
        model = ParentProfile
        fields = [
            'id',
            'user',
            'user_id',
            'occupation',
            'phone_number'
        ]
        read_only_fields = ['id']


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
        
        return data
