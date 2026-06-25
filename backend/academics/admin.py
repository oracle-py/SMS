from django.contrib import admin
from .models import (
    AcademicSession,
    Semester,
    Level,
    Course,
    StudentEnrollment,
    CourseRegistration,
    Grade,
    Attendance,
)


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    """Admin configuration for Academic Session model."""
    
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date')
    search_fields = ('name',)
    ordering = ('-is_active', '-start_date')
    
    fieldsets = (
        ('Session Information', {
            'fields': ('name', 'start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    """Admin configuration for Semester model."""
    
    list_display = ('name', 'session', 'get_session_dates')
    list_filter = ('name', 'session')
    search_fields = ('session__name',)
    ordering = ('session', 'name')
    
    def get_session_dates(self, obj):
        return f"{obj.session.start_date} to {obj.session.end_date}"
    get_session_dates.short_description = 'Session Dates'


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Admin configuration for Level model."""
    
    list_display = ('name', 'get_course_count')
    search_fields = ('name',)
    ordering = ('name',)
    
    def get_course_count(self, obj):
        return obj.courses.count()
    get_course_count.short_description = 'Number of Courses'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""
    
    list_display = ('course_code', 'course_title', 'credit_unit', 'level', 'semester', 'is_active')
    list_filter = ('level', 'semester', 'is_active', 'credit_unit')
    search_fields = ('course_code', 'course_title')
    ordering = ('course_code',)
    
    fieldsets = (
        ('Course Information', {
            'fields': ('course_code', 'course_title', 'credit_unit')
        }),
        ('Classification', {
            'fields': ('level', 'semester')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for Student Enrollment model."""
    
    list_display = ('student', 'level', 'session', 'enrollment_date')
    list_filter = ('level', 'session', 'enrollment_date')
    search_fields = ('student__user__username', 'student__user__email', 'student__student_id')
    ordering = ('-enrollment_date',)
    
    fieldsets = (
        ('Enrollment Details', {
            'fields': ('student', 'level', 'session')
        }),
        ('Timestamp', {
            'fields': ('enrollment_date',)
        }),
    )


@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    """Admin configuration for Course Registration model."""
    
    list_display = ('student', 'course', 'session', 'semester', 'is_carryover', 'registration_date')
    list_filter = ('is_carryover', 'session', 'semester', 'registration_date')
    search_fields = ('student__user__username', 'course__course_code', 'course__course_title')
    ordering = ('-registration_date',)
    
    fieldsets = (
        ('Registration Details', {
            'fields': ('student', 'course', 'session', 'semester')
        }),
        ('Status', {
            'fields': ('is_carryover',)
        }),
        ('Timestamp', {
            'fields': ('registration_date',)
        }),
    )


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Admin configuration for Grade model."""
    
    list_display = ('get_student', 'get_course', 'get_session', 'get_semester', 'score', 'letter_grade', 'grade_point', 'created_at')
    list_filter = ('letter_grade', 'grade_point', 'created_at', 'registration__course__level')
    search_fields = ('registration__student__user__username', 'registration__course__course_code', 'registration__course__course_title')
    ordering = ('-created_at',)
    readonly_fields = ('letter_grade', 'grade_point', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Grade Information', {
            'fields': ('registration', 'score')
        }),
        ('Calculated Fields', {
            'fields': ('letter_grade', 'grade_point')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_student(self, obj):
        return obj.registration.student.user.username
    get_student.short_description = 'Student'
    
    def get_course(self, obj):
        return f"{obj.registration.course.course_code} - {obj.registration.course.course_title}"
    get_course.short_description = 'Course'
    
    def get_session(self, obj):
        return obj.registration.session.name
    get_session.short_description = 'Session'
    
    def get_semester(self, obj):
        return obj.registration.semester.get_name_display()
    get_semester.short_description = 'Semester'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for Attendance model."""
    
    list_display = ('student', 'course', 'date', 'status', 'created_at')
    list_filter = ('status', 'date', 'course', 'created_at')
    search_fields = ('student__user__username', 'course__course_code', 'course__course_title')
    ordering = ('-date', '-created_at')
    
    fieldsets = (
        ('Attendance Details', {
            'fields': ('student', 'course', 'date', 'status')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
