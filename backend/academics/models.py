from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Faculty(models.Model):
    """
    Represents a faculty in the institution.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Faculty Name',
        help_text='e.g., Engineering, Science, Arts'
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Faculty Code',
        help_text='e.g., ENG, SCI, ART'
    )
    
    class Meta:
        db_table = 'faculties'
        ordering = ['name']
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Department(models.Model):
    """
    Represents a department within a faculty.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Department Name',
        help_text='e.g., Computer Engineering, Physics'
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Department Code',
        help_text='e.g., CPE, PHY'
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name='Faculty'
    )
    
    class Meta:
        db_table = 'departments'
        unique_together = ['name', 'faculty']
        ordering = ['faculty', 'name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def faculty_name(self):
        return self.faculty.name


class Programme(models.Model):
    """
    Represents an academic programme offered by a department.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Programme Name',
        help_text='e.g., B.Eng Computer Engineering, B.Sc Physics'
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Programme Code',
        help_text='e.g., CPE-001, PHY-001'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='programmes',
        verbose_name='Department'
    )
    duration_years = models.PositiveIntegerField(
        default=4,
        verbose_name='Duration (Years)',
        help_text='Programme duration in years'
    )
    total_credit_units = models.PositiveIntegerField(
        default=120,
        verbose_name='Total Credit Units',
        help_text='Total credit units required for graduation'
    )
    
    class Meta:
        db_table = 'programmes'
        ordering = ['department', 'name']
        verbose_name = 'Programme'
        verbose_name_plural = 'Programmes'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def faculty(self):
        return self.department.faculty


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
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='Department'
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
    
    @property
    def faculty(self):
        return self.department.faculty
    
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
    GRADE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=GRADE_STATUS_CHOICES,
        default='pending',
        verbose_name='Status',
        help_text='Grade approval status'
    )
    submitted_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_grades',
        verbose_name='Submitted By',
        help_text='Lecturer who submitted the grade'
    )
    approved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_grades',
        verbose_name='Approved By',
        help_text='Admin who approved the grade'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Approved At'
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
    remarks = models.TextField(
        blank=True,
        verbose_name='Remarks',
        help_text='Optional remarks for the attendance record'
    )
    recorded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_attendances',
        verbose_name='Recorded By',
        help_text='User who recorded this attendance'
    )
    recorded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Recorded At'
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


class CourseAssignment(models.Model):
    """
    Represents the assignment of a lecturer to a course for a specific session and semester.
    Supports multiple lecturers per course across different sessions/semesters.
    """
    ASSIGNMENT_ROLE_CHOICES = [
        ('primary', 'Primary Lecturer'),
        ('assistant', 'Assistant Lecturer'),
        ('coordinator', 'Course Coordinator'),
        ('lab_instructor', 'Lab Instructor'),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Course'
    )
    lecturer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='course_assignments',
        verbose_name='Lecturer',
        limit_choices_to={'role': 'lecturer'}
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='course_assignments',
        verbose_name='Academic Session'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='course_assignments',
        verbose_name='Semester'
    )
    role = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_ROLE_CHOICES,
        default='primary',
        verbose_name='Role'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Assigned At'
    )
    
    class Meta:
        db_table = 'course_assignments'
        unique_together = ['course', 'lecturer', 'session', 'semester']
        ordering = ['session', 'semester', 'course']
        verbose_name = 'Course Assignment'
        verbose_name_plural = 'Course Assignments'
    
    def __str__(self):
        return f"{self.course.course_code} - {self.lecturer.get_full_name()} ({self.get_role_display()}) - {self.session.name}"


class Timetable(models.Model):
    """
    Represents a scheduled class for a course assignment.
    Links to CourseAssignment to derive lecturer information.
    """
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]
    
    course_assignment = models.ForeignKey(
        CourseAssignment,
        on_delete=models.CASCADE,
        related_name='timetables',
        verbose_name='Course Assignment'
    )
    day_of_week = models.CharField(
        max_length=20,
        choices=DAY_CHOICES,
        verbose_name='Day of Week'
    )
    start_time = models.TimeField(
        verbose_name='Start Time'
    )
    end_time = models.TimeField(
        verbose_name='End Time'
    )
    venue = models.CharField(
        max_length=100,
        verbose_name='Venue',
        help_text='e.g., Room 101, Lab 3, Auditorium'
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='timetables',
        verbose_name='Academic Session'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='timetables',
        verbose_name='Semester'
    )
    
    class Meta:
        db_table = 'timetables'
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Timetable'
        verbose_name_plural = 'Timetables'
    
    def __str__(self):
        return f"{self.course_assignment.course.course_code} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
    
    @property
    def course(self):
        return self.course_assignment.course
    
    @property
    def lecturer(self):
        return self.course_assignment.lecturer


class Announcement(models.Model):
    """
    Represents institutional announcements.
    Can be targeted to specific user roles.
    """
    AUDIENCE_CHOICES = [
        ('all', 'All Users'),
        ('student', 'Students Only'),
        ('lecturer', 'Lecturers Only'),
        ('parent', 'Parents Only'),
        ('admin', 'Admin Only'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Title'
    )
    content = models.TextField(
        verbose_name='Content'
    )
    target_audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default='all',
        verbose_name='Target Audience'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_announcements',
        verbose_name='Created By'
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
        db_table = 'announcements'
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
    
    def __str__(self):
        return f"{self.title} ({self.get_target_audience_display()})"


class Result(models.Model):
    """
    Represents student academic results for a course.
    Supports pending and approved workflow.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Student',
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Course'
    )
    lecturer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_results',
        verbose_name='Lecturer',
        limit_choices_to={'role': 'lecturer'}
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Academic Session'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Semester'
    )
    ca_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='CA Score',
        help_text='Continuous Assessment score (max 40)'
    )
    exam_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Exam Score',
        help_text='Examination score (max 60)'
    )
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Total Score',
        help_text='Total score (CA + Exam)'
    )
    grade = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name='Grade'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='Remarks'
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Submitted At'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Approved At'
    )
    approved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_results',
        verbose_name='Approved By',
        limit_choices_to={'role': 'admin'}
    )
    
    class Meta:
        db_table = 'results'
        unique_together = ['student', 'course', 'session', 'semester']
        ordering = ['-session', 'semester', 'course', 'student']
        verbose_name = 'Result'
        verbose_name_plural = 'Results'
    
    def __str__(self):
        return f"{self.student.username} - {self.course.course_code} - {self.total_score} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Calculate total score
        self.total_score = self.ca_score + self.exam_score
        # Auto-calculate grade based on total score
        self.grade = self.calculate_grade(self.total_score)
        super().save(*args, **kwargs)
    
    @staticmethod
    def calculate_grade(score):
        """Calculate grade based on total score."""
        if score >= 70:
            return 'A'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C'
        elif score >= 45:
            return 'D'
        elif score >= 40:
            return 'E'
        else:
            return 'F'
    
    @property
    def grade_point(self):
        """Calculate grade point based on grade (5-point scale)."""
        grade_points = {'A': 5.0, 'B': 4.0, 'C': 3.0, 'D': 2.0, 'E': 1.0, 'F': 0.0}
        return grade_points.get(self.grade, 0.0)
    
    @property
    def quality_point(self):
        """Calculate quality point (grade_point × course credit_unit)."""
        return self.grade_point * (self.course.credit_unit or 0)


class CGPARecord(models.Model):
    """
    Records CGPA calculations for tracking student academic performance history.
    """
    student = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='cgpa_records',
        verbose_name='Student',
        limit_choices_to={'role': 'student'}
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='cgpa_records',
        verbose_name='Academic Session'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='cgpa_records',
        verbose_name='Semester',
        null=True,
        blank=True
    )
    cgpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name='CGPA',
        help_text='Cumulative Grade Point Average'
    )
    total_credit_units = models.PositiveIntegerField(
        verbose_name='Total Credit Units'
    )
    total_quality_points = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total Quality Points'
    )
    calculated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Calculated At'
    )
    
    class Meta:
        db_table = 'cgpa_records'
        unique_together = ['student', 'session', 'semester']
        ordering = ['-session', 'semester', '-calculated_at']
        verbose_name = 'CGPA Record'
        verbose_name_plural = 'CGPA Records'
    
    def __str__(self):
        semester_str = f" - {self.semester.get_name_display()}" if self.semester else ""
        return f"{self.student.username} - {self.session.name}{semester_str} - CGPA: {self.cgpa}"


class ActivityLog(models.Model):
    """
    Enhanced activity logging for tracking system actions.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='User'
    )
    action = models.CharField(
        max_length=100,
        verbose_name='Action',
        help_text='e.g., REGISTER_STUDENT, APPROVE_RESULT'
    )
    entity_type = models.CharField(
        max_length=50,
        verbose_name='Entity Type',
        help_text='e.g., Student, Course, Grade'
    )
    entity_id = models.PositiveIntegerField(
        verbose_name='Entity ID'
    )
    description = models.TextField(
        verbose_name='Description',
        help_text='Human-readable description of the action'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} - {self.entity_type}"


class AuditTrail(models.Model):
    """
    Detailed audit trail for tracking data changes.
    Stores old and new data for important actions.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_trails',
        verbose_name='User'
    )
    action = models.CharField(
        max_length=50,
        verbose_name='Action',
        help_text='e.g., CREATE, UPDATE, DELETE'
    )
    entity_type = models.CharField(
        max_length=50,
        verbose_name='Entity Type'
    )
    entity_id = models.PositiveIntegerField(
        verbose_name='Entity ID'
    )
    old_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Old Data'
    )
    new_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name='New Data'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp'
    )
    
    class Meta:
        db_table = 'audit_trails'
        ordering = ['-timestamp']
        verbose_name = 'Audit Trail'
        verbose_name_plural = 'Audit Trails'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} - {self.entity_type}"


class Notification(models.Model):
    """
    System notifications for users.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('academic', 'Academic'),
        ('administrative', 'Administrative'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Title'
    )
    message = models.TextField(
        verbose_name='Message'
    )
    recipient = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Recipient'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='info',
        verbose_name='Type'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Read'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Read At'
    )
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


class Permission(models.Model):
    """
    Permissions for RBAC system.
    Defines granular permissions that can be assigned to roles.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Permission Name',
        help_text='e.g., register_student, approve_results, delete_users'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    module = models.CharField(
        max_length=50,
        verbose_name='Module',
        help_text='e.g., students, courses, grades, users'
    )
    
    class Meta:
        db_table = 'permissions'
        ordering = ['module', 'name']
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
    
    def __str__(self):
        return f"{self.name} ({self.module})"


class Role(models.Model):
    """
    Roles for RBAC system.
    Roles can have multiple permissions.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Role Name',
        help_text='e.g., Registrar, HOD, Dean, ICT Admin'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    permissions = models.ManyToManyField(
        Permission,
        related_name='roles',
        verbose_name='Permissions'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'roles'
        ordering = ['name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.name
    
    def has_permission(self, permission_name):
        """Check if role has a specific permission."""
        return self.permissions.filter(name=permission_name).exists()
