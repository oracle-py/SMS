from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access control."""
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('admin', 'Admin'),
        ('lecturer', 'Lecturer'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=False)  # Personal email, not unique
    username = models.CharField(max_length=150, unique=True)  # School email, unique identifier
    phone = models.CharField(max_length=20, blank=True, null=True)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    roles = models.ManyToManyField(
        'academics.Role',
        related_name='users',
        blank=True,
        verbose_name='RBAC Roles',
        help_text='Additional roles for granular permissions'
    )
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']
    
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
    
    @property
    def is_lecturer(self):
        return self.role == 'lecturer'
    
    def has_permission(self, permission_name):
        """Check if user has a specific permission through their roles."""
        return self.roles.filter(permissions__name=permission_name).exists()


class StudentProfile(models.Model):
    """Extended profile for student users."""
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='Gender')
    date_of_birth = models.DateField()
    grade_level = models.IntegerField()
    programme = models.ForeignKey(
        'academics.Programme',
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name='Programme',
        null=True,
        blank=True
    )
    enrollment_date = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.student_id}"
    
    @property
    def department(self):
        return self.programme.department if self.programme else None
    
    @property
    def faculty(self):
        return self.programme.faculty if self.programme else None
    
    def calculate_session_cgpa(self, session):
        """Calculate CGPA for a specific academic session."""
        from academics.models import Result
        results = Result.objects.filter(
            student=self.user,
            session=session,
            status='approved'
        )
        total_quality_points = sum(r.quality_point for r in results)
        total_credit_units = sum(r.course.credit_unit for r in results if r.course.credit_unit)
        return round(total_quality_points / total_credit_units, 2) if total_credit_units > 0 else 0.0
    
    def calculate_semester_cgpa(self, session, semester):
        """Calculate CGPA for a specific semester."""
        from academics.models import Result
        results = Result.objects.filter(
            student=self.user,
            session=session,
            semester=semester,
            status='approved'
        )
        total_quality_points = sum(r.quality_point for r in results)
        total_credit_units = sum(r.course.credit_unit for r in results if r.course.credit_unit)
        return round(total_quality_points / total_credit_units, 2) if total_credit_units > 0 else 0.0
    
    def calculate_cumulative_cgpa(self):
        """Calculate cumulative CGPA across all sessions."""
        from academics.models import Result
        results = Result.objects.filter(
            student=self.user,
            status='approved'
        )
        total_quality_points = sum(r.quality_point for r in results)
        total_credit_units = sum(r.course.credit_unit for r in results if r.course.credit_unit)
        return round(total_quality_points / total_credit_units, 2) if total_credit_units > 0 else 0.0


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


class LecturerProfile(models.Model):
    """Extended profile for lecturer users."""
    RANK_CHOICES = [
        ('graduate_assistant', 'Graduate Assistant'),
        ('assistant_lecturer', 'Assistant Lecturer'),
        ('lecturer_ii', 'Lecturer II'),
        ('lecturer_i', 'Lecturer I'),
        ('senior_lecturer', 'Senior Lecturer'),
        ('associate_professor', 'Associate Professor'),
        ('professor', 'Professor'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('visiting', 'Visiting'),
        ('contract', 'Contract'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
    staff_id = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Staff ID')
    rank = models.CharField(max_length=30, choices=RANK_CHOICES, verbose_name='Academic Rank')
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        verbose_name='Employment Type'
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.PROTECT,
        related_name='lecturers',
        verbose_name='Department',
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(verbose_name='Date of Birth')
    date_of_employment = models.DateField(auto_now_add=True, verbose_name='Date of Employment')
    
    class Meta:
        db_table = 'lecturer_profiles'
        verbose_name = 'Lecturer Profile'
        verbose_name_plural = 'Lecturer Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.staff_id}"
    
    @property
    def faculty(self):
        return self.department.faculty
