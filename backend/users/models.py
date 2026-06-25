from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access control."""
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_parent(self):
        return self.role == 'parent'
    
    @property
    def is_admin_user(self):
        return self.role == 'admin'


class StudentProfile(models.Model):
    """Extended profile for student users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    grade_level = models.IntegerField()
    enrollment_date = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.student_id}"


class ParentProfile(models.Model):
    """Extended profile for parent users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'parent_profiles'
        verbose_name = 'Parent Profile'
        verbose_name_plural = 'Parent Profiles'
    
    def __str__(self):
        return f"{self.user.username} - Parent"


class ParentStudentRelation(models.Model):
    """Relationship between parents and students."""
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, related_name='student_relations')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='parent_relations')
    relationship_type = models.CharField(max_length=20, choices=[
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
    ])
    
    class Meta:
        db_table = 'parent_student_relations'
        unique_together = ['parent', 'student']
        verbose_name = 'Parent-Student Relation'
        verbose_name_plural = 'Parent-Student Relations'
    
    def __str__(self):
        return f"{self.parent.user.username} - {self.student.user.username} ({self.relationship_type})"
