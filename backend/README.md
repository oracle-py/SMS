# Student Monitoring System

A production-quality Django backend for monitoring student academic performance with role-based access control.

## 🔷 Project Overview

This system provides three user roles:
- **Student**: View grades, attendance, and GPA
- **Parent/Guardian**: Monitor child's academic performance  
- **Admin**: Manage students, parents, courses, grades, and attendance

## 🔷 Technology Stack

- **Backend**: Django 5.2+
- **API**: Django REST Framework (DRF)
- **Authentication**: JWT (SimpleJWT)
- **Database**: SQLite (development), PostgreSQL (production)
- **Python**: 3.10+

## 🔷 Project Structure

```
school-monitoring-system/
├── school_monitoring_system/     # Main Django project
├── users/                         # User authentication and roles
├── academics/                     # Courses, grades, attendance
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables
└── manage.py                     # Django management script
```

## 🔷 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file with:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser --username admin --email admin@school.com --role admin
```

### 5. Run Development Server
```bash
python manage.py runserver
```

### 6. Access Admin Panel
Visit `http://127.0.0.1:8000/admin/`
- Username: `admin`
- Password: `admin123` (or whatever you set)

## 🔷 User Model Features

### Custom User Model
- Extends Django's AbstractUser
- Role-based access: student, parent, admin
- Email-based authentication
- Role-specific profile models

### User Profiles
- **StudentProfile**: Student ID, grade level, enrollment info
- **ParentProfile**: Contact information, occupation
- **ParentStudentRelation**: Links parents to students

## 🔷 Django Apps

### Users App (`users/`)
- Custom user authentication
- Role management
- Profile models
- Admin interface

### Academics App (`academics/`)
- Course management
- Grade tracking
- Attendance records
- GPA calculation (coming soon)

## 🔷 API Configuration

- **Authentication**: JWT tokens
- **Permissions**: Role-based access control
- **Pagination**: PageNumberPagination (20 items/page)
- **Token Lifetime**: 60 minutes access, 1 day refresh

## 🔷 Admin Interface

The admin panel provides:
- User management with role filtering
- Student profile management
- Parent profile management
- Parent-student relationship management

## 🔷 Development Workflow

1. **Project Setup** ✅
2. **Custom User Model** ✅
3. **Core Academic Models** (next)
4. **API Endpoints** (next)
5. **Permissions & Security** (next)
6. **GPA Calculation** (next)

## 🔷 Security Features

- JWT-based authentication
- Role-based permissions
- Input validation
- Secure password handling
- CSRF protection

## 🔷 Next Steps

The foundation is complete. Next phases include:
1. Academic models (Course, Grade, Attendance)
2. REST API endpoints
3. Role-based permissions
4. GPA calculation service
5. API documentation

## 🔷 Commands Reference

```bash
# Development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Check project
python manage.py check
```
