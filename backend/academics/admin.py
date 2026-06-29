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
    Faculty,
    Department,
    Programme,
    CourseAssignment,
    Timetable,
    Announcement,
    ActivityLog,
    AuditTrail,
    Notification,
    Permission,
    Role,
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
    
    list_display = ('student', 'course', 'date', 'status', 'recorded_by', 'recorded_at')
    list_filter = ('status', 'date', 'course', 'recorded_at')
    search_fields = ('student__user__username', 'course__course_code', 'course__course_title')
    ordering = ('-date', '-recorded_at')
    
    fieldsets = (
        ('Attendance Details', {
            'fields': ('student', 'course', 'date', 'status', 'remarks')
        }),
        ('Recording Info', {
            'fields': ('recorded_by', 'recorded_at')
        }),
    )


class DepartmentInline(admin.TabularInline):
    """Inline admin for Department within Faculty."""
    model = Department
    extra = 0
    fields = ('name', 'code')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """Admin configuration for Faculty model."""
    
    list_display = ('name', 'code', 'get_department_count')
    search_fields = ('name', 'code')
    ordering = ('name',)
    
    fieldsets = (
        ('Faculty Information', {
            'fields': ('name', 'code')
        }),
    )
    
    inlines = [DepartmentInline]
    
    def save_model(self, request, obj, form, change):
        """Override save_model to handle saving with validation."""
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            form.add_error(None, f"Error saving faculty: {str(e)}")
            raise
    
    def get_department_count(self, obj):
        return obj.departments.count()
    get_department_count.short_description = 'Departments'


class ProgrammeInline(admin.TabularInline):
    """Inline admin for Programme within Department."""
    model = Programme
    extra = 0
    fields = ('name', 'code', 'duration_years', 'total_credit_units')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for Department model."""
    
    list_display = ('name', 'code', 'faculty', 'get_programme_count', 'get_course_count')
    list_filter = ('faculty',)
    search_fields = ('name', 'code', 'faculty__name')
    ordering = ('faculty', 'name')
    
    fieldsets = (
        ('Department Information', {
            'fields': ('name', 'code', 'faculty')
        }),
    )
    
    inlines = [ProgrammeInline]
    
    def save_model(self, request, obj, form, change):
        """Override save_model to handle saving with validation."""
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except Exception as e:
            form.add_error(None, f"Error saving department: {str(e)}")
            raise
    
    def get_programme_count(self, obj):
        return obj.programmes.count()
    get_programme_count.short_description = 'Programmes'
    
    def get_course_count(self, obj):
        return obj.courses.count()
    get_course_count.short_description = 'Courses'


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    """Admin configuration for Programme model."""
    
    list_display = ('name', 'code', 'department', 'duration_years', 'total_credit_units', 'get_student_count')
    list_filter = ('department', 'duration_years')
    search_fields = ('name', 'code', 'department__name')
    ordering = ('department', 'name')
    
    fieldsets = (
        ('Programme Information', {
            'fields': ('name', 'code', 'department')
        }),
        ('Programme Details', {
            'fields': ('duration_years', 'total_credit_units')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to handle saving with validation."""
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except Exception as e:
            form.add_error(None, f"Error saving programme: {str(e)}")
            raise
    
    def get_student_count(self, obj):
        return obj.students.count()
    get_student_count.short_description = 'Students'


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for Course Assignment model."""
    
    list_display = ('course', 'lecturer', 'session', 'semester', 'role', 'assigned_at')
    list_filter = ('role', 'session', 'semester')
    search_fields = ('course__course_code', 'lecturer__username', 'lecturer__first_name', 'lecturer__last_name')
    ordering = ('session', 'semester', 'course')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    """Admin configuration for Timetable model."""
    
    list_display = ('course', 'lecturer', 'day_of_week', 'start_time', 'end_time', 'venue', 'session', 'semester')
    list_filter = ('day_of_week', 'session', 'semester')
    search_fields = ('course__course_code', 'venue', 'lecturer__username')
    ordering = ('day_of_week', 'start_time')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Admin configuration for Announcement model."""
    
    list_display = ('title', 'target_audience', 'is_active', 'created_by', 'created_at')
    list_filter = ('target_audience', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Announcement Details', {
            'fields': ('title', 'content', 'target_audience', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin configuration for Activity Log model."""
    
    list_display = ('user', 'action', 'entity_type', 'entity_id', 'ip_address', 'created_at')
    list_filter = ('action', 'entity_type', 'created_at')
    search_fields = ('user__username', 'action', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    """Admin configuration for Audit Trail model."""
    
    list_display = ('user', 'action', 'entity_type', 'entity_id', 'timestamp')
    list_filter = ('action', 'entity_type', 'timestamp')
    search_fields = ('user__username', 'action', 'entity_type')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    ordering = ('-created_at',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin configuration for Permission model."""
    
    list_display = ('name', 'module', 'description')
    list_filter = ('module',)
    search_fields = ('name', 'module', 'description')
    ordering = ('module', 'name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin configuration for Role model."""
    
    list_display = ('name', 'description', 'get_permission_count', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    filter_horizontal = ('permissions',)
    
    def get_permission_count(self, obj):
        return obj.permissions.count()
    get_permission_count.short_description = 'Permissions'
