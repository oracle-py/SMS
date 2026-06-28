from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, ParentProfile, ParentStudentRelation, LecturerProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Student Profile."""
    
    list_display = ('user', 'student_id', 'programme', 'grade_level', 'enrollment_date')
    list_filter = ('grade_level', 'enrollment_date', 'programme')
    search_fields = ('user__username', 'user__email', 'student_id')
    ordering = ('student_id',)
    
    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'student_id', 'date_of_birth', 'grade_level', 'programme')
        }),
        ('Enrollment', {
            'fields': ('enrollment_date',)
        }),
    )


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Parent Profile."""
    
    list_display = ('user', 'phone_number', 'occupation')
    search_fields = ('user__username', 'user__email', 'phone_number')
    ordering = ('user__username',)
    
    fieldsets = (
        ('Parent Information', {
            'fields': ('user', 'phone_number', 'occupation')
        }),
    )


@admin.register(ParentStudentRelation)
class ParentStudentRelationAdmin(admin.ModelAdmin):
    """Admin configuration for Parent-Student Relations."""
    
    list_display = ('parent', 'student', 'relationship_type')
    list_filter = ('relationship_type',)
    search_fields = ('parent__user__username', 'student__user__username')
    ordering = ('parent__user__username',)
    
    fieldsets = (
        ('Relationship', {
            'fields': ('parent', 'student', 'relationship_type')
        }),
    )


@admin.register(LecturerProfile)
class LecturerProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Lecturer Profile."""
    
    list_display = ('user', 'staff_id', 'rank', 'employment_type', 'department', 'date_of_employment')
    list_filter = ('rank', 'employment_type', 'department')
    search_fields = ('user__username', 'user__email', 'staff_id')
    ordering = ('staff_id',)
    
    fieldsets = (
        ('Lecturer Information', {
            'fields': ('user', 'staff_id', 'rank', 'employment_type', 'department')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth',)
        }),
        ('Employment', {
            'fields': ('date_of_employment',)
        }),
    )
