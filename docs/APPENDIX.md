# APPENDICES

## APPENDIX A: SYSTEM DIRECTORY STRUCTURE

This appendix shows the overall organization of the School Monitoring System project.

```
School-Monitoring-System/
│
├── backend/
│   ├── academics/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   └── urls.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── management/
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   └── urls.py
│   ├── school_monitoring_system/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── .env
│   ├── db.sqlite3
│   ├── manage.py
│   ├── requirements.txt
│   ├── schema.yml
│   └── build.sh
│
├── frontend/
│   ├── public/
│   │   └── vite.svg
│   ├── src/
│   │   ├── api/
│   │   │   └── axios.js
│   │   ├── components/
│   │   │   ├── attendance/
│   │   │   │   └── AttendanceTable.jsx
│   │   │   ├── results/
│   │   │   │   └── ResultsTable.jsx
│   │   │   └── drawer.css
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── layouts/
│   │   │   ├── DashboardLayout.jsx
│   │   │   ├── DashboardLayout.css
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Sidebar.css
│   │   │   ├── Topbar.jsx
│   │   │   └── navigation.js
│   │   ├── pages/
│   │   │   ├── admin/
│   │   │   │   ├── AdminDashboard.jsx
│   │   │   │   ├── Courses.jsx
│   │   │   │   ├── Parents.jsx
│   │   │   │   ├── Students.jsx
│   │   │   │   ├── Teachers.jsx
│   │   │   │   ├── admin.css
│   │   │   │   └── components/
│   │   │   │       ├── RegisterStudentDrawer.jsx
│   │   │   │       ├── RegisterLecturerDrawer.jsx
│   │   │   │       └── ReviewResultsDrawer.jsx
│   │   │   ├── student/
│   │   │   │   ├── StudentAttendance.jsx
│   │   │   │   ├── StudentCourses.jsx
│   │   │   │   ├── StudentDashboard.jsx
│   │   │   │   ├── StudentLecturers.jsx
│   │   │   │   ├── StudentResults.jsx
│   │   │   │   ├── StudentTimetable.jsx
│   │   │   │   └── student.css
│   │   │   ├── Login.jsx
│   │   │   ├── UnderDevelopment.jsx
│   │   │   └── Unauthorized.jsx
│   │   ├── routes/
│   │   │   └── AppRoutes.jsx
│   │   ├── services/
│   │   │   └── studentService.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json
│
└── docs/
    ├── APPENDIX.md
    └── API_DOCUMENTATION.md
```

---

## APPENDIX B: DATABASE SCHEMA

### User Table
```
id              INTEGER (Primary Key, Auto-increment)
username        VARCHAR(150) (Unique)
email           VARCHAR(254) (Unique)
password        VARCHAR(128)
role            VARCHAR(10) (Choices: student, parent, admin, lecturer)
phone           VARCHAR(20) (Nullable)
other_name      VARCHAR(100) (Nullable)
first_name      VARCHAR(150)
last_name       VARCHAR(150)
is_active       BOOLEAN (Default: True)
is_staff        BOOLEAN (Default: False)
is_superuser    BOOLEAN (Default: False)
date_joined     DATETIME (Auto-generated)
last_login      DATETIME (Nullable)
```

### StudentProfile Table
```
id                  INTEGER (Primary Key, Auto-increment)
user_id             INTEGER (Foreign Key → User.id)
student_id          VARCHAR(20) (Unique, Nullable)
matric_number       VARCHAR(30) (Unique, Nullable)
date_of_birth       DATE
grade_level         INTEGER
programme_id        INTEGER (Foreign Key → Programme.id, Nullable)
enrollment_date     DATE (Auto-generated)
```

### ParentProfile Table
```
id              INTEGER (Primary Key, Auto-increment)
user_id         INTEGER (Foreign Key → User.id)
phone_number    VARCHAR(20) (Nullable)
occupation      VARCHAR(100) (Nullable)
```

### LecturerProfile Table
```
id                  INTEGER (Primary Key, Auto-increment)
user_id             INTEGER (Foreign Key → User.id)
staff_id            VARCHAR(20) (Unique, Nullable)
department_id       INTEGER (Foreign Key → Department.id, Nullable)
employment_type     VARCHAR(50) (Default: full_time)
date_of_birth       DATE (Nullable)
```

### ParentStudentRelation Table
```
id                  INTEGER (Primary Key, Auto-increment)
parent_id           INTEGER (Foreign Key → ParentProfile.id)
student_id          INTEGER (Foreign Key → StudentProfile.id)
relationship_type   VARCHAR(50) (Default: Parent)
created_at          DATETIME (Auto-generated)
```

### Faculty Table
```
id      INTEGER (Primary Key, Auto-increment)
name    VARCHAR(100) (Unique)
code    VARCHAR(10) (Unique)
```

### Department Table
```
id          INTEGER (Primary Key, Auto-increment)
name        VARCHAR(100)
code        VARCHAR(10) (Unique)
faculty_id  INTEGER (Foreign Key → Faculty.id)
```

### Programme Table
```
id                      INTEGER (Primary Key, Auto-increment)
name                    VARCHAR(200)
code                    VARCHAR(20) (Unique)
department_id           INTEGER (Foreign Key → Department.id)
duration_years          INTEGER (Default: 4)
total_credit_units      INTEGER (Default: 120)
```

### AcademicSession Table
```
id          INTEGER (Primary Key, Auto-increment)
name        VARCHAR(20) (Unique)
start_date  DATE
end_date    DATE
is_active   BOOLEAN (Default: False)
```

### Semester Table
```
id          INTEGER (Primary Key, Auto-increment)
name        VARCHAR(50)
session_id  INTEGER (Foreign Key → AcademicSession.id)
```

### Level Table
```
id      INTEGER (Primary Key, Auto-increment)
name    VARCHAR(50)
```

### Course Table
```
id              INTEGER (Primary Key, Auto-increment)
course_code     VARCHAR(20) (Unique)
course_title    VARCHAR(200)
credit_unit     INTEGER
level_id        INTEGER (Foreign Key → Level.id)
semester_id     INTEGER (Foreign Key → Semester.id)
is_active       BOOLEAN (Default: True)
```

### StudentEnrollment Table
```
id              INTEGER (Primary Key, Auto-increment)
student_id      INTEGER (Foreign Key → StudentProfile.id)
level_id        INTEGER (Foreign Key → Level.id)
session_id      INTEGER (Foreign Key → AcademicSession.id)
enrollment_date DATE (Auto-generated)
```

### CourseRegistration Table
```
id              INTEGER (Primary Key, Auto-increment)
student_id      INTEGER (Foreign Key → StudentProfile.id)
course_id       INTEGER (Foreign Key → Course.id)
session_id      INTEGER (Foreign Key → AcademicSession.id)
semester_id     INTEGER (Foreign Key → Semester.id)
registered_at   DATETIME (Auto-generated)
```

### Grade Table
```
id              INTEGER (Primary Key, Auto-increment)
student_id      INTEGER (Foreign Key → StudentProfile.id)
course_id       INTEGER (Foreign Key → Course.id)
score           DECIMAL(5, 2)
grade           VARCHAR(2)
status          VARCHAR(20) (Choices: pending, approved, rejected)
graded_at       DATETIME (Auto-generated)
```

### Attendance Table
```
id              INTEGER (Primary Key, Auto-increment)
student_id      INTEGER (Foreign Key → StudentProfile.id)
course_id       INTEGER (Foreign Key → Course.id)
date            DATE
status          VARCHAR(20) (Choices: present, absent, late)
marked_at       DATETIME (Auto-generated)
```

---

## APPENDIX C: SAMPLE DJANGO MODELS

### User Model
```python
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
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    roles = models.ManyToManyField(
        'academics.Role',
        related_name='users',
        blank=True,
        verbose_name='RBAC Roles',
        help_text='Additional roles for granular permissions'
    )
    
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
    
    @property
    def is_lecturer(self):
        return self.role == 'lecturer'
```

### StudentProfile Model
```python
class StudentProfile(models.Model):
    """Extended profile for student users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
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
```

### Faculty Model
```python
class Faculty(models.Model):
    """Represents a faculty in the institution."""
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
```

### Department Model
```python
class Department(models.Model):
    """Represents a department within a faculty."""
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
```

### Programme Model
```python
class Programme(models.Model):
    """Represents an academic programme offered by a department."""
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
```

### Course Model
```python
class Course(models.Model):
    """Represents an academic course."""
    course_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Course Code'
    )
    course_title = models.CharField(
        max_length=200,
        verbose_name='Course Title'
    )
    credit_unit = models.PositiveIntegerField(
        default=2,
        verbose_name='Credit Unit'
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
        verbose_name='Active'
    )
    
    class Meta:
        db_table = 'courses'
        ordering = ['course_code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
    
    def __str__(self):
        return f"{self.course_code} - {self.course_title}"
```

---

## APPENDIX D: SAMPLE API CONFIGURATION

### Main URL Configuration (school_monitoring_system/urls.py)
```python
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def root_view(request):
    """Root path handler that returns API information."""
    return JsonResponse({
        'message': 'School Monitoring System API',
        'version': 'v1',
        'endpoints': {
            'api': '/api/',
            'admin': '/admin/',
            'docs': '/api/docs/',
            'redoc': '/api/redoc/',
            'schema': '/api/schema/'
        }
    })


urlpatterns = [
    path('', root_view),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # API documentation endpoints
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### API URL Configuration (api/urls.py)
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'lecturers', LecturerViewSet, basename='lecturer')
router.register(r'programmes', ProgrammeViewSet, basename='programme')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'faculties', FacultyViewSet, basename='faculty')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'sessions', AcademicSessionViewSet, basename='session')
router.register(r'semesters', SemesterViewSet, basename='semester')
router.register(r'levels', LevelViewSet, basename='level')

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('stats/public/', PublicStatsView.as_view(), name='public_stats'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('', include(router.urls)),
]
```

---

## APPENDIX E: SAMPLE API RESPONSES

### Login Response
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIwMDAwMDAwLCJpYXQiOjE3MTk5MTM2MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.signed_token_here",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiZnJlc2giLCJleHAiOjE3MjA1MDAwMDAsImlhdCI6MTcxOTkxMzYwMCwianRpIjoiOTg3NjU0MzIxMCIsInVzZXJfaWQiOjF9.signed_token_here",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@school.edu",
        "role": "admin",
        "first_name": "Admin",
        "last_name": "Administrator"
    }
}
```

### Public Statistics Response
```json
{
    "total_students": 1250,
    "total_lecturers": 85,
    "total_courses": 156,
    "total_departments": 12,
    "trust_score": 94.5
}
```

### Admin Dashboard Response
```json
{
    "statistics": {
        "total_students": 1250,
        "total_lecturers": 85,
        "total_courses": 156,
        "total_departments": 12,
        "active_sessions": 1
    },
    "recent_registrations": [
        {
            "id": 1250,
            "student_name": "John Doe",
            "matric_number": "2025/001",
            "programme": "B.Eng Computer Engineering",
            "registration_date": "2025-01-15"
        }
    ],
    "pending_approvals": 15,
    "recent_activity": [
        {
            "action": "Student Registration",
            "user": "Admin",
            "timestamp": "2025-01-15T10:30:00Z"
        }
    ]
}
```

### Students List Response
```json
{
    "count": 1250,
    "next": "http://api.example.com/api/students/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": {
                "id": 1,
                "username": "johndoe",
                "email": "john.doe@school.edu",
                "first_name": "John",
                "last_name": "Doe"
            },
            "student_id": "2025/001",
            "matric_number": "2025/001",
            "programme": {
                "id": 1,
                "name": "B.Eng Computer Engineering",
                "code": "CPE-001"
            },
            "grade_level": 100,
            "department": "Computer Engineering",
            "faculty": "Engineering",
            "enrollment_date": "2025-01-15"
        }
    ]
}
```

### Student Registration Response
```json
{
    "id": 1251,
    "user": {
        "id": 1251,
        "username": "janedoe",
        "email": "jane.doe@school.edu",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "student"
    },
    "student_id": "2025/002",
    "matric_number": "2025/002",
    "programme": {
        "id": 1,
        "name": "B.Eng Computer Engineering"
    },
    "grade_level": 100,
    "enrollment_date": "2025-01-16"
}
```

### Lecturers List Response
```json
{
    "count": 85,
    "results": [
        {
            "id": 1,
            "user": {
                "id": 10,
                "username": "drsmith",
                "email": "dr.smith@school.edu",
                "first_name": "Robert",
                "last_name": "Smith"
            },
            "staff_id": "LEC-001",
            "department": {
                "id": 1,
                "name": "Computer Engineering"
            },
            "employment_type": "full_time"
        }
    ]
}
```

### Programmes List Response
```json
{
    "count": 25,
    "results": [
        {
            "id": 1,
            "name": "B.Eng Computer Engineering",
            "code": "CPE-001",
            "department": {
                "id": 1,
                "name": "Computer Engineering",
                "faculty": "Engineering"
            },
            "duration_years": 5,
            "total_credit_units": 150
        }
    ]
}
```

---

## APPENDIX F: JWT AUTHENTICATION FLOW

```
┌─────────────────┐
│   User Login    │
│   (Frontend)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  POST /api/auth/token/          │
│  {                              │
│    "email": "user@school.edu",  │
│    "password": "password"      │
│  }                              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Django REST API                │
│  - Validate credentials         │
│  - Generate JWT tokens          │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Response:                      │
│  {                              │
│    "access": "jwt_token",       │
│    "refresh": "refresh_token",  │
│    "user": {...}                │
│  }                              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Frontend stores tokens in      │
│  localStorage                   │
│  - access_token                 │
│  - refresh_token                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Authenticated API Requests     │
│  - Add Authorization header     │
│    "Bearer {access_token}"      │
│  - Make API calls               │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Token Expires?                 │
│  - POST /api/auth/token/refresh/│
│  - Get new access token         │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Logout                         │
│  - Clear localStorage           │
│  - Clear sidebar state          │
└─────────────────────────────────┘
```

---

## APPENDIX G: SAMPLE FRONTEND COMPONENTS

### AuthContext Component
```javascript
import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('access');
        if (token) {
            // Validate token and fetch user data
            fetchUserData();
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (email, password) => {
        const response = await api.post('/auth/token/', { email, password });
        localStorage.setItem('access', response.data.access);
        localStorage.setItem('refresh', response.data.refresh);
        setUser(response.data.user);
        return response.data;
    };

    const logout = () => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sidebarOpen');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
```

### ProtectedRoute Component
```javascript
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, allowedRoles }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!user) {
        return <Navigate to="/" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(user.role)) {
        return <Navigate to="/unauthorized" replace />;
    }

    return children;
};

export default ProtectedRoute;
```

### DashboardLayout Component
```javascript
import { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function DashboardLayout({ children }) {
    const [sidebarOpen, setSidebarOpen] = useState(() => {
        const saved = localStorage.getItem("sidebarOpen");
        if (saved !== null) return saved === "true";
        return false;
    });

    useEffect(() => {
        localStorage.setItem("sidebarOpen", sidebarOpen);
    }, [sidebarOpen]);

    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    return (
        <div className="dashboard-layout">
            <Sidebar
                isOpen={sidebarOpen}
                toggleSidebar={toggleSidebar}
            />
            <div className="dashboard-main">
                <Topbar toggleSidebar={toggleSidebar} />
                <main className="dashboard-content">
                    {children}
                </main>
            </div>
        </div>
    );
}
```

### RegisterStudentDrawer Component (Auto-fill Logic)
```javascript
function handleChange(e) {
    const { name, value } = e.target;
    
    setFormData(prev => {
        const newData = {
            ...prev,
            [name]: value
        };

        // Auto-fill entry level based on student type
        if (name === 'student_type') {
            if (value === 'UTME') {
                newData.entry_level = '100';
            } else if (value === 'Direct Entry') {
                newData.entry_level = '200';
            } else if (value === 'Transfer') {
                newData.entry_level = '300';
            }
        }

        return newData;
    });
}
```

### Students Page Component
```javascript
import { useState, useEffect } from "react";
import DashboardLayout from "../../layouts/DashboardLayout";
import api from "../../api/axios";
import RegisterStudentDrawer from "./components/RegisterStudentDrawer";

function Students() {
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [drawerOpen, setDrawerOpen] = useState(false);

    useEffect(() => {
        fetchStudents();
    }, []);

    async function fetchStudents() {
        setLoading(true);
        try {
            const response = await api.get("/students/");
            setStudents(response.data.results || response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    const handleDrawerClose = () => {
        setDrawerOpen(false);
        fetchStudents();
    };

    return (
        <DashboardLayout>
            <div className="ad-page">
                <div className="students-header-box">
                    <div className="students-header-content">
                        <h1>Students</h1>
                        <p>Manage registered students across the institution.</p>
                    </div>
                    <button 
                        className="ad-button-primary"
                        onClick={() => setDrawerOpen(true)}
                    >
                        Add Student
                    </button>
                </div>
                {/* Students table */}
            </div>
            <RegisterStudentDrawer 
                open={drawerOpen} 
                onClose={handleDrawerClose} 
            />
        </DashboardLayout>
    );
}

export default Students;
```

---

## APPENDIX H: AXIOS API CONFIGURATION

### Axios Instance Setup (src/api/axios.js)
```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh');
                const response = await axios.post('/api/auth/token/refresh/', {
                    refresh: refreshToken
                });

                const { access } = response.data;
                localStorage.setItem('access', access);

                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
            } catch (refreshError) {
                localStorage.removeItem('access');
                localStorage.removeItem('refresh');
                window.location.href = '/';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;
```

---

## APPENDIX I: BACKEND REQUIREMENTS

### requirements.txt
```
Django>=4.2.0
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.2.0
python-decouple>=3.8
django-filter>=24.0
drf-spectacular>=0.27.0
django-cors-headers>=4.0.0
gunicorn
whitenoise
psycopg2-binary
```

### Environment Variables (.env)
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend-domain.com
```

---

## APPENDIX J: FRONTEND DEPENDENCIES

### package.json
```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "framer-motion": "^12.42.0",
    "lucide-react": "^1.22.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-icons": "^5.6.0",
    "react-router-dom": "^6.26.1"
  },
  "devDependencies": {
    "@eslint/js": "^9.11.1",
    "@types/react": "^18.3.10",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.2",
    "eslint": "^9.11.1",
    "eslint-plugin-react": "^7.37.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.12",
    "globals": "^15.9.0",
    "vite": "^5.4.8"
  }
}
```

### Environment Variables (.env)
```
VITE_API_URL=http://localhost:8000/api
```

---

## APPENDIX K: API ENDPOINTS DOCUMENTATION

### Authentication Endpoints

#### POST /api/auth/token/
Login endpoint to obtain JWT tokens.

**Request Body:**
```json
{
    "email": "user@school.edu",
    "password": "password"
}
```

**Response:**
```json
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 1,
        "username": "user",
        "email": "user@school.edu",
        "role": "student",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

#### POST /api/auth/token/refresh/
Refresh access token using refresh token.

**Request Body:**
```json
{
    "refresh": "jwt_refresh_token"
}
```

**Response:**
```json
{
    "access": "new_jwt_access_token"
}
```

### Statistics Endpoints

#### GET /api/stats/public/
Public statistics for login page (no authentication required).

**Response:**
```json
{
    "total_students": 1250,
    "total_lecturers": 85,
    "total_courses": 156,
    "total_departments": 12,
    "trust_score": 94.5
}
```

#### GET /api/dashboard/admin/
Admin dashboard statistics (requires admin role).

**Response:**
```json
{
    "statistics": {
        "total_students": 1250,
        "total_lecturers": 85,
        "total_courses": 156,
        "total_departments": 12
    },
    "recent_registrations": [...],
    "pending_approvals": 15
}
```

### Student Endpoints

#### GET /api/students/
List all students (requires admin role).

**Query Parameters:**
- `page`: Page number for pagination
- `search`: Search by name, email, or matric number

**Response:**
```json
{
    "count": 1250,
    "next": "...",
    "previous": null,
    "results": [...]
}
```

#### POST /api/students/
Register a new student (requires admin role).

**Request Body:**
```json
{
    "user_data": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@school.edu",
        "phone": "+1234567890"
    },
    "gender": "Male",
    "date_of_birth": "2000-01-01",
    "student_id": "2025/001",
    "grade_level": 100,
    "programme": 1
}
```

#### GET /api/students/{id}/
Retrieve specific student details.

#### PUT /api/students/{id}/
Update student information.

#### DELETE /api/students/{id}/
Delete a student.

### Lecturer Endpoints

#### GET /api/lecturers/
List all lecturers (requires admin role).

#### POST /api/lecturers/
Register a new lecturer (requires admin role).

**Request Body:**
```json
{
    "user_data": {
        "first_name": "Robert",
        "last_name": "Smith",
        "email": "robert.smith@school.edu"
    },
    "staff_id": "LEC-001",
    "department": 1,
    "employment_type": "full_time"
}
```

### Programme Endpoints

#### GET /api/programmes/
List all programmes.

**Response:**
```json
{
    "count": 25,
    "results": [
        {
            "id": 1,
            "name": "B.Eng Computer Engineering",
            "code": "CPE-001",
            "department": {
                "id": 1,
                "name": "Computer Engineering",
                "faculty": "Engineering"
            },
            "duration_years": 5,
            "total_credit_units": 150
        }
    ]
}
```

### Department Endpoints

#### GET /api/departments/
List all departments.

#### POST /api/departments/
Create a new department (requires admin role).

### Faculty Endpoints

#### GET /api/faculties/
List all faculties.

#### POST /api/faculties/
Create a new faculty (requires admin role).

### Course Endpoints

#### GET /api/courses/
List all courses.

#### POST /api/courses/
Create a new course (requires admin/lecturer role).

---

## APPENDIX L: SYSTEM INTERFACES

### Interface Screenshots

**Note:** The following sections describe the implemented interfaces. Actual screenshots should be captured and inserted here in the final documentation.

#### L.1 Login Page
- Features login form with email and password fields
- Displays live statistics cards (Students, Lecturers, Trust Score)
- Demo account buttons for quick testing
- Gradient background with decorative elements
- Responsive design for mobile devices

#### L.2 Admin Dashboard
- Hero section with gradient background
- Statistics cards showing live data
- Quick action buttons for common tasks
- Latest registration display
- Department count with live data
- Recent activity feed

#### L.3 Students Management Page
- Custom-designed header box with gradient (purple/indigo)
- Icon-based header with glassmorphism effects
- Responsive table with pronounced gradient headers
- Table columns: Student, Matric No, Email, Programme, Level, Status, Actions
- Search functionality
- Add Student button linked to RegisterStudentDrawer
- Mobile-responsive with horizontal scrolling

#### L.4 Lecturers Management Page
- Similar structure to Students page
- Table columns: Staff ID, Name, Email, Department, Actions
- Search and filter functionality
- Terminology updated to "Lecturers"

#### L.5 Courses Management Page
- Course listing with code, title, credit units
- Filter by level and semester
- Add/Edit/Delete functionality

#### L.6 Register Student Drawer
- Slide-out drawer from right side
- Personal Information section (name, gender, date of birth)
- Contact Information section (email, phone)
- Academic Information section (programme, entry level, student type)
- Auto-fill entry level based on student type (UTME=100, Direct Entry=200, Transfer=300)
- Entry level field disabled with gray background
- Parent/Guardian Information section
- Form validation and error handling

#### L.7 Register Lecturer Drawer
- Similar structure to RegisterStudentDrawer
- Fields for personal information, department, employment type
- Staff ID generation option

#### L.8 Student Dashboard
- Hero banner with student greeting
- Academic standing display (CGPA, attendance, carryovers)
- Profile card with student details
- Quick access to results, attendance, courses
- Responsive design

#### L.9 Parent Dashboard
- List of linked children/students
- Quick access to children's results and attendance
- Profile information

#### L.10 Responsive Mobile Views
- Sidebar collapses to hamburger menu
- Tables scroll horizontally
- Header boxes stack vertically
- Touch-friendly buttons and inputs
- Adaptive font sizes and spacing

### CSS Styling Highlights

#### Students Header Box Styling
```css
.students-header-box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 28px 32px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    color: white;
    position: relative;
    overflow: hidden;
}
```

#### Table Header Styling
```css
.ad-table thead {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
}

.ad-table th {
    padding: 18px 24px;
    text-align: left;
    font-size: 13px;
    text-transform: uppercase;
    color: #ffffff;
    letter-spacing: 0.06em;
    font-weight: 600;
}
```

#### Responsive Table Styling
```css
@media(max-width: 768px) {
    .ad-card {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }

    .ad-table {
        min-width: 600px;
    }

    .students-header-box {
        flex-direction: column;
        align-items: flex-start;
        gap: 20px;
    }
}
```

---

## APPENDIX M: DJANGO ADMIN CONFIGURATION

### Admin Configuration for Department Model
```python
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
    
    def get_programme_count(self, obj):
        return obj.programmes.count()
    get_programme_count.short_description = 'Programmes'
    
    def get_course_count(self, obj):
        return obj.courses.count()
    get_course_count.short_description = 'Courses'
```

### Inline Configuration for Programme
```python
class ProgrammeInline(admin.TabularInline):
    """Inline admin for Programme within Department."""
    model = Programme
    extra = 0
    fields = ('name', 'code', 'duration_years', 'total_credit_units')
```

---

## APPENDIX N: DEPLOYMENT CONFIGURATION

### Backend Deployment (Render.com)

#### entrypoint.sh
```bash
#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn school_monitoring_system.wsgi:application --bind 0.0.0.0:$PORT
```

#### build.sh
```bash
pip install -r requirements.txt
python manage.py collectstatic
```

### Frontend Deployment (Vercel/Render)

#### vercel.json
```json
{
    "buildCommand": "npm run build",
    "outputDirectory": "dist",
    "devCommand": "npm run dev"
}
```

---

## APPENDIX O: ERROR HANDLING

### Frontend Error Handling Example
```javascript
const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
        const response = await api.post('/students/', {
            user_data: {
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email
            },
            grade_level: parseInt(formData.entry_level),
            programme: formData.programme
        });
        
        alert('Student registered successfully!');
        setFormData(initialData);
        onClose();
    } catch (error) {
        console.error('Error registering student:', error);
        const errorMessage = error.response?.data?.detail || 
                            error.response?.data?.error ||
                            'Failed to register student';
        alert(`Error: ${errorMessage}`);
    } finally {
        setLoading(false);
    }
};
```

### Backend Error Handling Example
```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code
        }
        response.data = custom_response_data
    
    return response
```

---

**END OF APPENDICES**
