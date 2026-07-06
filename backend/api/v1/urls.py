"""
URL configuration for API v1.

This module defines the URL patterns for version 1 of the API,
including authentication, user, academic, and dashboard endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    CurrentUserView,
)
from users.viewsets import (
    StudentProfileViewSet,
    ParentProfileViewSet,
    ParentStudentRelationViewSet,
    LecturerProfileViewSet,
)
from academics.viewsets import (
    AcademicSessionViewSet,
    SemesterViewSet,
    LevelViewSet,
    CourseViewSet,
    StudentEnrollmentViewSet,
    CourseRegistrationViewSet,
    GradeViewSet,
    AttendanceViewSet,
    FacultyViewSet,
    DepartmentViewSet,
    ProgrammeViewSet,
    CourseAssignmentViewSet,
    TimetableViewSet,
    AnnouncementViewSet,
    ResultViewSet,
    ActivityLogViewSet,
)
from api.views.student_dashboard import (
    StudentDashboardView,
    StudentResultsView,
    StudentAttendanceView,
)
from api.views.parent_dashboard import (
    ParentDashboardView,
    ParentWardDetailView,
)
from api.views.admin_dashboard import (
    AdminDashboardView,
)
from api.views.stats import PublicStatsView

app_name = 'api_v1'

# Create router for ViewSets
router = DefaultRouter()

# User ViewSets
router.register(r'students', StudentProfileViewSet, basename='student')
router.register(r'parents', ParentProfileViewSet, basename='parent')
router.register(r'parent-student-relations', ParentStudentRelationViewSet, basename='parent-student-relation')
router.register(r'lecturers', LecturerProfileViewSet, basename='lecturer')

# Academic ViewSets
router.register(r'sessions', AcademicSessionViewSet, basename='session')
router.register(r'semesters', SemesterViewSet, basename='semester')
router.register(r'levels', LevelViewSet, basename='level')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', StudentEnrollmentViewSet, basename='enrollment')
router.register(r'registrations', CourseRegistrationViewSet, basename='registration')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

# Organization ViewSets
router.register(r'faculties', FacultyViewSet, basename='faculty')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'programmes', ProgrammeViewSet, basename='programme')

# Course Assignment ViewSets
router.register(r'course-assignments', CourseAssignmentViewSet, basename='course-assignment')
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'results', ResultViewSet, basename='result')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    
    # Public statistics endpoint
    path('stats/public/', PublicStatsView.as_view(), name='public-stats'),
    
    # Student dashboard endpoints
    path('student/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('student/results/', StudentResultsView.as_view(), name='student-results'),
    path('student/attendance/', StudentAttendanceView.as_view(), name='student-attendance'),
    
    # Parent dashboard endpoints
    path('parent/dashboard/', ParentDashboardView.as_view(), name='parent-dashboard'),
    path('parent/wards/<int:student_id>/', ParentWardDetailView.as_view(), name='parent-ward-detail'),
    
    # Admin dashboard endpoints
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # ViewSet endpoints
    path('', include(router.urls)),
]
