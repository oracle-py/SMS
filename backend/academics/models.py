from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AcademicSession(models.Model):
    """
    Represents an academic session (e.g., 2025/2026).
    Only one session can be active at a time.
    """
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Session Name',
        help_text='e.g., 2025/2026'
    )
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')
    is_active = models.BooleanField(
        default=False,
        verbose_name='Active Session',
        help_text='Only one session can be active at a time'
    )
    
    class Meta:
        db_table = 'academic_sessions'
        ordering = ['-is_active', '-start_date']
        verbose_name = 'Academic Session'
        verbose_name_plural = 'Academic Sessions'
    
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"
    
    def clean(self):
        """Ensure only one session is active at a time."""
        if self.is_active:
            active_sessions = AcademicSession.objects.filter(
                is_active=True
            ).exclude(pk=self.pk)
            if active_sessions.exists():
                raise ValidationError(
                    'Only one academic session can be active at a time. '
                    'Please deactivate the current active session first.'
                )
        
        if self.end_date <= self.start_date:
            raise ValidationError(
                'End date must be after start date.'
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Semester(models.Model):
    """
    Represents a semester within an academic session.
    """
    SEMESTER_CHOICES = [
        ('first', 'First Semester'),
        ('second', 'Second Semester'),
    ]
    
    name = models.CharField(
        max_length=20,
        choices=SEMESTER_CHOICES,
        verbose_name='Semester'
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='semesters',
        verbose_name='Academic Session'
    )
    
    class Meta:
        db_table = 'semesters'
        unique_together = ['name', 'session']
        ordering = ['session', 'name']
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.session.name}"


class Level(models.Model):
    """
    Represents academic levels (100 Level, 200 Level, etc.).
    """
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Level Name',
        help_text='e.g., 100 Level, 200 Level'
    )
    
    class Meta:
        db_table = 'levels'
        ordering = ['name']
        verbose_name = 'Level'
        verbose_name_plural = 'Levels'
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Represents a course offered by the institution.
    """
    course_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Course Code',
        help_text='e.g., CSC101, MTH201'
    )
    course_title = models.CharField(
        max_length=200,
        verbose_name='Course Title'
    )
    credit_unit = models.PositiveIntegerField(
        verbose_name='Credit Unit',
        help_text='Must be a positive integer'
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Level'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Semester'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Course'
    )
    
    class Meta:
        db_table = 'courses'
        ordering = ['course_code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
    
    def __str__(self):
        return f"{self.course_code} - {self.course_title} ({self.credit_unit} units)"
    
    def clean(self):
        if self.credit_unit <= 0:
            raise ValidationError(
                'Credit unit must be a positive integer.'
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class StudentEnrollment(models.Model):
    """
    Represents a student's enrollment into a level for a specific session.
    """
    student = models.ForeignKey(
        'users.StudentProfile',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Student'
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name='student_enrollments',
        verbose_name='Level'
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='student_enrollments',
        verbose_name='Academic Session'
    )
    enrollment_date = models.DateField(
        auto_now_add=True,
        verbose_name='Enrollment Date'
    )
    
    class Meta:
        db_table = 'student_enrollments'
        unique_together = ['student', 'session']
        ordering = ['-enrollment_date']
        verbose_name = 'Student Enrollment'
        verbose_name_plural = 'Student Enrollments'
    
    def __str__(self):
        return f"{self.student.user.username} - {self.level.name} - {self.session.name}"


class CourseRegistration(models.Model):
    """
    Represents courses registered by a student for a specific session and semester.
    """
    student = models.ForeignKey(
        'users.StudentProfile',
        on_delete=models.CASCADE,
        related_name='course_registrations',
        verbose_name='Student'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Course'
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='course_registrations',
        verbose_name='Academic Session'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='course_registrations',
        verbose_name='Semester'
    )
    is_carryover = models.BooleanField(
        default=False,
        verbose_name='Carryover',
        help_text='Mark if this is a carryover course'
    )
    registration_date = models.DateField(
        auto_now_add=True,
        verbose_name='Registration Date'
    )
    
    class Meta:
        db_table = 'course_registrations'
        unique_together = ['student', 'course', 'session', 'semester']
        ordering = ['-registration_date']
        verbose_name = 'Course Registration'
        verbose_name_plural = 'Course Registrations'
    
    def __str__(self):
        status = 'Carryover' if self.is_carryover else 'Regular'
        return f"{self.student.user.username} - {self.course.course_code} ({status})"


class Grade(models.Model):
    """
    Represents a student's grade for a specific course registration.
    Automatically calculates letter grade and grade point based on score.
    
    Linked to CourseRegistration to support multiple course attempts,
    carry-over tracking, and proper academic history.
    """
    GRADE_SCALE = {
        'A': (70, 100, 5),
        'B': (60, 69, 4),
        'C': (50, 59, 3),
        'D': (45, 49, 2),
        'E': (40, 44, 1),
        'F': (0, 39, 0),
    }
    
    registration = models.OneToOneField(
        CourseRegistration,
        on_delete=models.CASCADE,
        related_name='grade',
        verbose_name='Course Registration',
        help_text='The specific course registration attempt for this grade'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Score',
        help_text='Score between 0 and 100'
    )
    letter_grade = models.CharField(
        max_length=1,
        editable=False,
        verbose_name='Letter Grade'
    )
    grade_point = models.IntegerField(
        editable=False,
        verbose_name='Grade Point'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    class Meta:
        db_table = 'grades'
        ordering = ['-created_at']
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
    
    def __str__(self):
        """Display grade with student, course, session, semester, and grade."""
        return (
            f"{self.registration.student.user.username} - "
            f"{self.registration.course.course_code} - "
            f"{self.registration.session.name} - "
            f"{self.registration.semester.get_name_display()}: "
            f"{self.score} ({self.letter_grade})"
        )
    
    @property
    def student(self):
        """Convenience property to access student through registration."""
        return self.registration.student
    
    @property
    def course(self):
        """Convenience property to access course through registration."""
        return self.registration.course
    
    @property
    def session(self):
        """Convenience property to access session through registration."""
        return self.registration.session
    
    @property
    def semester(self):
        """Convenience property to access semester through registration."""
        return self.registration.semester
    
    def calculate_grade(self):
        """Calculate letter grade and grade point based on score."""
        score = float(self.score)
        
        for letter, (min_score, max_score, point) in self.GRADE_SCALE.items():
            if min_score <= score <= max_score:
                return letter, point
        
        return 'F', 0
    
    def clean(self):
        if self.score < 0 or self.score > 100:
            raise ValidationError(
                'Score must be between 0 and 100.'
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        self.letter_grade, self.grade_point = self.calculate_grade()
        super().save(*args, **kwargs)


class Attendance(models.Model):
    """
    Represents student attendance for a specific course on a specific date.
    """
    ATTENDANCE_STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]
    
    student = models.ForeignKey(
        'users.StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Student'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Course'
    )
    date = models.DateField(
        verbose_name='Date'
    )
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS_CHOICES,
        verbose_name='Status'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'attendances'
        unique_together = ['student', 'course', 'date']
        ordering = ['-date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.course_code} - {self.date} ({self.get_status_display()})"
