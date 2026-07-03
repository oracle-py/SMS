# Frontend API Guide - School Monitoring System

**Version:** 1.0  
**Last Updated:** 2026-06-18  
**Backend Version:** Django 5.2+ with Django REST Framework

---

## 1. Project Overview

### Authentication Method
- **JWT (JSON Web Tokens)** using `rest_framework_simplejwt`
- Token-based stateless authentication
- Access token lifetime: 60 minutes
- Refresh token lifetime: 1 day
- Refresh token rotation enabled for security

### JWT Token Strategy
- **Access Token:** Short-lived token (60 min) for API requests
- **Refresh Token:** Long-lived token (1 day) for obtaining new access tokens
- **Token Blacklisting:** Refresh tokens are blacklisted on logout
- **Custom Claims:** Tokens include `role` and `username` claims for frontend use

### User Roles Supported

#### Admin
- Full system access
- Can manage all resources (students, parents, courses, grades, attendance)
- Can view all dashboards and academic records
- Can create and modify academic structure (sessions, semesters, levels, courses)

#### Student
- Can view own academic dashboard
- Can view own grades, attendance, and course registrations
- Cannot access other students' data
- Cannot modify academic records (read-only)

#### Parent
- Can view dashboard of linked students (wards)
- Can view academic performance of linked students
- Cannot access students not linked to them
- Cannot modify academic records (read-only)

---

## 2. Authentication Flow

### Base URL
```
http://localhost:8001/api/v1
```

### 2.1 POST /api/v1/auth/login/

Authenticate user and obtain JWT tokens.

**URL:** `/api/v1/auth/login/`  
**HTTP Method:** `POST`  
**Required Headers:** None  
**Request Body:**

```json
{
  "email": "admin@school.edu",
  "password": "admin123"
}
```

**OR using username:**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Success Response (200 OK):**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@school.edu",
    "first_name": "Admin",
    "last_name": "Administrator",
    "role": "admin"
  },
  "profile": {
    "id": 1,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@school.edu",
      "first_name": "Admin",
      "last_name": "Administrator",
      "role": "admin"
    },
    "student_id": null,
    "date_of_birth": null,
    "grade_level": null,
    "enrollment_date": null,
    "age": null
  }
}
```

**Error Responses:**

- **400 Bad Request:** Invalid credentials or missing fields
```json
{
  "detail": "No active account found with the given credentials"
}
```

- **400 Bad Request:** Missing username or email
```json
{
  "detail": "Either username or email is required"
}
```

**Frontend Usage Notes:**
- Store both `access` and `refresh` tokens securely (e.g., localStorage or httpOnly cookies)
- Access token should be included in `Authorization: Bearer <access_token>` header for all protected requests
- Refresh token should be used to obtain new access tokens when the current one expires
- The `user` object contains basic user information for immediate display
- The `profile` object contains role-specific profile data (null for admin, populated for student/parent)

---

### 2.2 POST /api/v1/auth/refresh/

Refresh access token using refresh token.

**URL:** `/api/v1/auth/refresh/`  
**HTTP Method:** `POST`  
**Required Headers:** None  
**Request Body:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**

- **401 Unauthorized:** Invalid or expired refresh token
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

- **401 Unauthorized:** Blacklisted refresh token
```json
{
  "detail": "Token is blacklisted",
  "code": "token_not_valid"
}
```

**Frontend Usage Notes:**
- Implement automatic token refresh using axios interceptors
- When a 401 error occurs, attempt to refresh the access token
- If refresh fails, redirect to login page
- Store the new access token and retry the failed request
- Refresh token rotation is enabled, so you'll get a new refresh token on successful refresh

---

### 2.3 POST /api/v1/auth/logout/

Logout by blacklisting the refresh token.

**URL:** `/api/v1/auth/logout/`  
**HTTP Method:** `POST`  
**Required Headers:** `Authorization: Bearer <access_token>`  
**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "message": "Successfully logged out."
}
```

**Error Responses:**

- **400 Bad Request:** Missing refresh token
```json
{
  "success": false,
  "error": "Refresh token is required."
}
```

- **400 Bad Request:** Invalid or already blacklisted token
```json
{
  "success": false,
  "error": "Token is blacklisted"
}
```

**Frontend Usage Notes:**
- Call this endpoint when user logs out
- Clear stored tokens from storage after successful logout
- Redirect to login page
- Handle case where token is already blacklisted (treat as success)

---

### 2.4 GET /api/v1/auth/me/

Get current authenticated user information with profile data.

**URL:** `/api/v1/auth/me/`  
**HTTP Method:** `GET`  
**Required Headers:** `Authorization: Bearer <access_token>`  
**Request Body:** None

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@school.edu",
    "first_name": "Admin",
    "last_name": "Administrator",
    "role": "admin",
    "profile": null
  }
}
```

**Student Response Example:**

```json
{
  "success": true,
  "data": {
    "id": 2,
    "username": "student1",
    "email": "student1@school.edu",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "profile": {
      "id": 1,
      "user": {
        "id": 2,
        "username": "student1",
        "email": "student1@school.edu",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student"
      },
      "student_id": "STU/2024/001",
      "date_of_birth": "2000-01-01",
      "grade_level": 100,
      "enrollment_date": "2024-01-15",
      "age": 24
    }
  }
}
```

**Error Responses:**

- **401 Unauthorized:** Invalid or expired access token
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

- **500 Internal Server Error:** Server error
```json
{
  "success": false,
  "error": "An error occurred: <error message>"
}
```

**Frontend Usage Notes:**
- Use this endpoint to get current user information after login
- Call this endpoint on app initialization to restore user session
- Use the `role` field to determine which dashboard to show
- Use the `profile` data to display user-specific information
- Handle 401 errors by redirecting to login page

---

## 3. Role-Based Access Control

### RBAC Matrix

| Endpoint | Admin | Student | Parent |
| -------- | ----- | ------- | ------ |
| **Authentication** |
| POST /api/v1/auth/login/ | ✅ | ✅ | ✅ |
| POST /api/v1/auth/refresh/ | ✅ | ✅ | ✅ |
| POST /api/v1/auth/logout/ | ✅ | ✅ | ✅ |
| GET /api/v1/auth/me/ | ✅ | ✅ | ✅ |
| **Student Dashboard** |
| GET /api/v1/student/dashboard/ | ❌ | ✅ | ❌ |
| GET /api/v1/student/results/ | ❌ | ✅ | ❌ |
| GET /api/v1/student/attendance/ | ❌ | ✅ | ❌ |
| **Parent Dashboard** |
| GET /api/v1/parent/dashboard/ | ❌ | ❌ | ✅ |
| GET /api/v1/parent/wards/{id}/ | ❌ | ❌ | ✅ |
| **Student Resources** |
| GET /api/v1/students/ | ✅ | ❌ | ❌ |
| POST /api/v1/students/ | ✅ | ❌ | ❌ |
| GET /api/v1/students/{id}/ | ✅ | ✅ (own) | ✅ (linked) |
| PUT /api/v1/students/{id}/ | ✅ | ✅ (own) | ❌ |
| DELETE /api/v1/students/{id}/ | ✅ | ❌ | ❌ |
| **Parent Resources** |
| GET /api/v1/parents/ | ✅ | ❌ | ❌ |
| POST /api/v1/parents/ | ✅ | ❌ | ❌ |
| GET /api/v1/parents/{id}/ | ✅ | ✅ (own) | ❌ |
| PUT /api/v1/parents/{id}/ | ✅ | ✅ (own) | ❌ |
| DELETE /api/v1/parents/{id}/ | ✅ | ❌ | ❌ |
| **Parent-Student Relations** |
| GET /api/v1/parent-student-relations/ | ✅ | ✅ (own) | ✅ (own) |
| POST /api/v1/parent-student-relations/ | ✅ | ❌ | ❌ |
| GET /api/v1/parent-student-relations/{id}/ | ✅ | ✅ (own) | ✅ (own) |
| PUT /api/v1/parent-student-relations/{id}/ | ✅ | ❌ | ✅ (own) |
| DELETE /api/v1/parent-student-relations/{id}/ | ✅ | ❌ | ❌ |
| **Academic Sessions** |
| GET /api/v1/sessions/ | ✅ | ✅ | ✅ |
| POST /api/v1/sessions/ | ✅ | ❌ | ❌ |
| PUT /api/v1/sessions/{id}/ | ✅ | ❌ | ❌ |
| DELETE /api/v1/sessions/{id}/ | ✅ | ❌ | ❌ |
| **Semesters** |
| GET /api/v1/semesters/ | ✅ | ✅ | ✅ |
| POST /api/v1/semesters/ | ✅ | ❌ | ❌ |
| PUT /api/v1/semesters/{id}/ | ✅ | ❌ | ❌ |
| DELETE /api/v1/semesters/{id}/ | ✅ | ❌ | ❌ |
| **Levels** |
| GET /api/v1/levels/ | ✅ | ✅ | ✅ |
| POST /api/v1/levels/ | ✅ | ❌ | ❌ |
| PUT /api/v1/levels/{id}/ | ✅ | ❌ | ❌ |
| DELETE /api/v1/levels/{id}/ | ✅ | ❌ | ❌ |
| **Courses** |
| GET /api/v1/courses/ | ✅ | ✅ | ✅ |
| POST /api/v1/courses/ | ✅ | ❌ | ❌ |
| PUT /api/v1/courses/{id}/ | ✅ | ❌ | ❌ |
| DELETE /api/v1/courses/{id}/ | ✅ | ❌ | ❌ |
| **Student Enrollments** |
| GET /api/v1/enrollments/ | ✅ | ✅ (own) | ✅ (linked) |
| POST /api/v1/enrollments/ | ✅ | ❌ | ❌ |
| GET /api/v1/enrollments/{id}/ | ✅ | ✅ (own) | ✅ (linked) |
| PUT /api/v1/enrollments/{id}/ | ✅ | ❌ | ❌ |
| DELETE /api/v1/enrollments/{id}/ | ✅ | ❌ | ❌ |
| **Course Registrations** |
| GET /api/v1/registrations/ | ✅ | ✅ (own) | ✅ (linked) |
| POST /api/v1/registrations/ | ✅ | ❌ | ❌ |
| GET /api/v1/registrations/{id}/ | ✅ | ✅ (own) | ✅ (linked) |
| PUT /api/v1/registrations/{id}/ | ✅ | ❌ | ❌ |
| DELETE /api/v1/registrations/{id}/ | ✅ | ❌ | ❌ |
| **Grades** |
| GET /api/v1/grades/ | ✅ | ✅ (own) | ✅ (linked) |
| POST /api/v1/grades/ | ✅ | ❌ | ❌ |
| GET /api/v1/grades/{id}/ | ✅ | ✅ (own) | ✅ (linked) |
| PUT /api/v1/grades/{id}/ | ✅ | ❌ | ❌ |
| DELETE /api/v1/grades/{id}/ | ✅ | ❌ | ❌ |
| **Attendance** |
| GET /api/v1/attendance/ | ✅ | ✅ (own) | ✅ (linked) |
| POST /api/v1/attendance/ | ✅ | ❌ | ❌ |
| GET /api/v1/attendance/{id}/ | ✅ | ✅ (own) | ✅ (linked) |
| PUT /api/v1/attendance/{id}/ | ✅ | ❌ | ❌ |
| DELETE /api/v1/attendance/{id}/ | ✅ | ❌ | ❌ |

### Expected 401 Responses
- **When:** Access token is missing, invalid, or expired
- **Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```
or
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### Expected 403 Responses
- **When:** User is authenticated but lacks permission for the resource
- **Response:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Frontend Usage Notes:**
- Implement role-based route guards in React Router
- Use the `role` from `/api/v1/auth/me/` to determine accessible routes
- Handle 403 errors by showing "Access Denied" page or redirecting to appropriate dashboard
- Admin users should see admin panel with full CRUD capabilities
- Students should only see their own dashboard and academic records
- Parents should only see their linked students' data

---

## 4. Student Dashboard APIs

### 4.1 GET /api/v1/student/dashboard/

Get comprehensive academic summary for the authenticated student.

**URL:** `/api/v1/student/dashboard/`  
**HTTP Method:** `GET`  
**Required Headers:** `Authorization: Bearer <access_token>`  
**Request Body:** None

**Request Example:**
```bash
curl -X GET http://localhost:8000/api/v1/student/dashboard/ \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "student_info": {
      "name": "John Doe",
      "matric_number": "STU/2024/001",
      "level": 100
    },
    "cgpa": 3.75,
    "academic_standing": "Good Standing",
    "attendance_percentage": 92.5,
    "carryover_count": 0,
    "total_courses_registered": 5,
    "recent_results": [
      {
        "course_code": "CSC101",
        "course_title": "Introduction to Computer Science",
        "score": 85.0,
        "grade": "A",
        "session": "2024/2025",
        "semester": "First"
      },
      {
        "course_code": "MTH101",
        "course_title": "Mathematics I",
        "score": 78.0,
        "grade": "B",
        "session": "2024/2025",
        "semester": "First"
      }
    ]
  }
}
```

**Field Definitions:**

| Field | Type | Nullable | Description |
| ----- | ---- | -------- | ----------- |
| `success` | boolean | No | Always true for successful response |
| `data.student_info.name` | string | No | Student's full name |
| `data.student_info.matric_number` | string | No | Student's unique matric number (student_id) |
| `data.student_info.level` | integer | No | Student's current grade level (100, 200, etc.) |
| `data.cgpa` | float | No | Current Cumulative Grade Point Average (0.0 - 5.0) |
| `data.academic_standing` | string | No | Academic standing (e.g., "Good Standing", "Probation") |
| `data.attendance_percentage` | float | No | Overall attendance percentage (0.0 - 100.0) |
| `data.carryover_count` | integer | No | Number of carryover courses |
| `data.total_courses_registered` | integer | No | Total number of courses currently registered |
| `data.recent_results` | array | No | Array of recent grade records (max 5) |
| `data.recent_results[].course_code` | string | No | Course code (e.g., "CSC101") |
| `data.recent_results[].course_title` | string | No | Course title |
| `data.recent_results[].score` | float | No | Numeric score (0.0 - 100.0) |
| `data.recent_results[].grade` | string | No | Letter grade (A, B, C, D, F) |
| `data.recent_results[].session` | string | No | Academic session name |
| `data.recent_results[].semester` | string | No | Semester name (First, Second) |

**Error Responses:**

- **401 Unauthorized:** Not authenticated or wrong role
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **403 Forbidden:** Not a student
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **404 Not Found:** Student profile not found
```json
{
  "success": false,
  "error": "Student profile not found."
}
```

- **500 Internal Server Error:** Server error
```json
{
  "success": false,
  "error": "An error occurred: <error message>"
}
```

**Frontend Rendering Recommendations:**
- Display CGPA with color coding (green for ≥3.5, yellow for 2.5-3.49, red for <2.5)
- Show academic standing with badge (green for "Good Standing", red for "Probation")
- Display attendance percentage with progress bar (green for ≥75%, yellow for 50-74%, red for <50%)
- Show carryover count with warning badge if > 0
- Display recent results in a table with color-coded grades
- Cache dashboard data for 5 minutes (backend handles this)
- Refresh dashboard data when user navigates to dashboard page

---

### 4.2 GET /api/v1/student/results/

Get all grades for the authenticated student with optional filtering.

**URL:** `/api/v1/student/results/`  
**HTTP Method:** `GET`  
**Required Headers:** `Authorization: Bearer <access_token>`  
**Request Body:** None

**Query Parameters (Optional):**
- `session` - Filter by session ID (integer)
- `semester` - Filter by semester ID (integer)
- `course` - Filter by course ID (integer)

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/student/results/?session=1&semester=1" \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "course_code": "CSC101",
      "course_title": "Introduction to Computer Science",
      "score": 85.0,
      "letter_grade": "A",
      "grade_point": 5,
      "session": "2024/2025",
      "semester": "First",
      "credit_unit": 3
    },
    {
      "course_code": "MTH101",
      "course_title": "Mathematics I",
      "score": 78.0,
      "letter_grade": "B",
      "grade_point": 4,
      "session": "2024/2025",
      "semester": "First",
      "credit_unit": 4
    }
  ]
}
```

**Field Definitions:**

| Field | Type | Nullable | Description |
| ----- | ---- | -------- | ----------- |
| `success` | boolean | No | Always true for successful response |
| `data[].course_code` | string | No | Course code |
| `data[].course_title` | string | No | Course title |
| `data[].score` | float | No | Numeric score (0.0 - 100.0) |
| `data[].letter_grade` | string | No | Letter grade (A, B, C, D, F) |
| `data[].grade_point` | integer | No | Grade point (0 - 5) |
| `data[].session` | string | No | Academic session name |
| `data[].semester` | string | No | Semester name (First, Second) |
| `data[].credit_unit` | integer | No | Course credit units |

**Error Responses:**

- **401 Unauthorized:** Not authenticated or wrong role
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **403 Forbidden:** Not a student
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **404 Not Found:** Student profile not found
```json
{
  "success": false,
  "error": "Student profile not found."
}
```

- **500 Internal Server Error:** Server error
```json
{
  "success": false,
  "error": "An error occurred: <error message>"
}
```

**Frontend Rendering Recommendations:**
- Display results in a sortable table
- Add filters for session, semester, and course
- Color-code grades (A=green, B=blue, C=yellow, D=orange, F=red)
- Show credit units and calculate total credits
- Allow export to PDF or CSV
- Implement pagination for large result sets
- Show CGPA calculation summary at top

---

### 4.3 GET /api/v1/student/attendance/

Get attendance records for the authenticated student with optional filtering.

**URL:** `/api/v1/student/attendance/`  
**HTTP Method:** `GET`  
**Required Headers:** `Authorization: Bearer <access_token>`  
**Request Body:** None

**Query Parameters (Optional):**
- `course` - Filter by course ID (integer)
- `session` - Filter by session ID (integer)
- `semester` - Filter by semester ID (integer)

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/student/attendance/?course=1" \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "attendance_percentage": 92.5,
    "total_records": 40,
    "present_records": 37,
    "absent_records": 3,
    "records": [
      {
        "course": "CSC101",
        "course_title": "Introduction to Computer Science",
        "date": "2024-09-01",
        "status": "present",
        "remarks": ""
      },
      {
        "course": "CSC101",
        "course_title": "Introduction to Computer Science",
        "date": "2024-09-08",
        "status": "absent",
        "remarks": "Medical leave"
      }
    ]
  }
}
```

**Field Definitions:**

| Field | Type | Nullable | Description |
| ----- | ---- | -------- | ----------- |
| `success` | boolean | No | Always true for successful response |
| `data.attendance_percentage` | float | No | Overall attendance percentage (0.0 - 100.0) |
| `data.total_records` | integer | No | Total number of attendance records |
| `data.present_records` | integer | No | Number of present records |
| `data.absent_records` | integer | No | Number of absent records |
| `data.records` | array | No | Array of attendance records |
| `data.records[].course` | string | No | Course code |
| `data.records[].course_title` | string | No | Course title |
| `data.records[].date` | string (ISO date) | No | Date of attendance record (YYYY-MM-DD) |
| `data.records[].status` | string | No | Attendance status ("present" or "absent") |
| `data.records[].remarks` | string | Yes | Optional remarks for the attendance record |

**Error Responses:**

- **401 Unauthorized:** Not authenticated or wrong role
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **403 Forbidden:** Not a student
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **404 Not Found:** Student profile not found
```json
{
  "success": false,
  "error": "Student profile not found."
}
```

- **500 Internal Server Error:** Server error
```json
{
  "success": false,
  "error": "An error occurred: <error message>"
}
```

**Frontend Rendering Recommendations:**
- Display attendance statistics with visual indicators (progress bars, pie charts)
- Show attendance calendar view with color-coded dates
- Display records in a table with filters for course, session, semester
- Color-code status (green=present, red=absent)
- Show remarks when available
- Calculate and display attendance trends over time
- Implement pagination for large record sets
- Allow export to PDF or CSV

---

## 5. Parent Dashboard APIs

### 5.1 GET /api/v1/parent/dashboard/

Get overview of all students linked to the authenticated parent.

**URL:** `/api/v1/parent/dashboard/`  
**HTTP Method:** `GET`  
**Required Headers:** `Authorization: Bearer <access_token>`  
**Request Body:** None

**Request Example:**
```bash
curl -X GET http://localhost:8000/api/v1/parent/dashboard/ \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "parent_name": "Richard Doe",
    "total_wards": 2,
    "wards": [
      {
        "student_id": 1,
        "name": "John Doe",
        "matric_number": "STU/2024/001",
        "level": 100,
        "cgpa": 3.75,
        "academic_standing": "Good Standing",
        "attendance_percentage": 92.5,
        "carryover_count": 0,
        "total_courses": 5,
        "relationship_type": "father"
      },
      {
        "student_id": 6,
        "name": "Sarah Jones",
        "matric_number": "STU/2024/006",
        "level": 100,
        "cgpa": 2.85,
        "academic_standing": "Good Standing",
        "attendance_percentage": 88.0,
        "carryover_count": 1,
        "total_courses": 5,
        "relationship_type": "father"
      }
    ]
  }
}
```

**Field Definitions:**

| Field | Type | Nullable | Description |
| ----- | ---- | -------- | ----------- |
| `success` | boolean | No | Always true for successful response |
| `data.parent_name` | string | No | Parent's full name |
| `data.total_wards` | integer | No | Total number of linked students |
| `data.wards` | array | No | Array of ward (student) information |
| `data.wards[].student_id` | integer | No | Student's database ID |
| `data.wards[].name` | string | No | Student's full name |
| `data.wards[].matric_number` | string | No | Student's matric number |
| `data.wards[].level` | integer | No | Student's grade level |
| `data.wards[].cgpa` | float | No | Student's CGPA |
| `data.wards[].academic_standing` | string | No | Academic standing |
| `data.wards[].attendance_percentage` | float | No | Attendance percentage |
| `data.wards[].carryover_count` | integer | No | Number of carryover courses |
| `data.wards[].total_courses` | integer | No | Total courses registered |
| `data.wards[].relationship_type` | string | No | Relationship (father, mother, guardian) |

**Error Responses:**

- **401 Unauthorized:** Not authenticated or wrong role
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **403 Forbidden:** Not a parent
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **404 Not Found:** Parent profile not found
```json
{
  "success": false,
  "error": "Parent profile not found."
}
```

- **500 Internal Server Error:** Server error
```json
{
  "success": false,
  "error": "An error occurred: <error message>"
}
```

**Frontend Rendering Recommendations:**
- Display wards in a card layout or grid
- Show quick stats for each ward (CGPA, attendance, carryovers)
- Color-code academic standing and attendance
- Add warning badges for carryovers
- Make each ward clickable to view detailed information
- Cache dashboard data for 5 minutes (backend handles this)
- Show relationship type for each ward

---

### 5.2 GET /api/v1/parent/wards/{id}/

Get detailed academic information for a specific linked student.

**URL:** `/api/v1/parent/wards/{student_id}/`  
**HTTP Method:** `GET`  
**Required Headers:** `Authorization: Bearer <access_token>`  
**Request Body:** None

**URL Parameters:**
- `student_id` - The ID of the student (integer, required)

**Request Example:**
```bash
curl -X GET http://localhost:8000/api/v1/parent/wards/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "student_info": {
      "student_id": 1,
      "name": "John Doe",
      "matric_number": "STU/2024/001",
      "level": 100,
      "email": "student1@school.edu"
    },
    "cgpa": 3.75,
    "academic_standing": "Good Standing",
    "attendance_percentage": 92.5,
    "carryover_count": 0,
    "total_courses": 5,
    "relationship_type": "father",
    "results": [
      {
        "course_code": "CSC101",
        "course_title": "Introduction to Computer Science",
        "score": 85.0,
        "letter_grade": "A",
        "grade_point": 5,
        "session": "2024/2025",
        "semester": "First",
        "credit_unit": 3
      }
    ],
    "carryovers": [],
    "attendance_records": [
      {
        "course": "CSC101",
        "course_title": "Introduction to Computer Science",
        "date": "2024-09-01",
        "status": "present",
        "remarks": ""
      }
    ]
  }
}
```

**Field Definitions:**

| Field | Type | Nullable | Description |
| ----- | ---- | -------- | ----------- |
| `success` | boolean | No | Always true for successful response |
| `data.student_info.student_id` | integer | No | Student's database ID |
| `data.student_info.name` | string | No | Student's full name |
| `data.student_info.matric_number` | string | No | Student's matric number |
| `data.student_info.level` | integer | No | Student's grade level |
| `data.student_info.email` | string | No | Student's email address |
| `data.cgpa` | float | No | Student's CGPA |
| `data.academic_standing` | string | No | Academic standing |
| `data.attendance_percentage` | float | No | Attendance percentage |
| `data.carryover_count` | integer | No | Number of carryover courses |
| `data.total_courses` | integer | No | Total courses registered |
| `data.relationship_type` | string | No | Relationship type |
| `data.results` | array | No | Array of grade records (max 10) |
| `data.results[].course_code` | string | No | Course code |
| `data.results[].course_title` | string | No | Course title |
| `data.results[].score` | float | No | Numeric score |
| `data.results[].letter_grade` | string | No | Letter grade |
| `data.results[].grade_point` | integer | No | Grade point |
| `data.results[].session` | string | No | Session name |
| `data.results[].semester` | string | No | Semester name |
| `data.results[].credit_unit` | integer | No | Credit units |
| `data.carryovers` | array | No | Array of carryover courses |
| `data.carryovers[].course_code` | string | No | Course code |
| `data.carryovers[].course_title` | string | No | Course title |
| `data.carryovers[].score` | float | No | Numeric score |
| `data.carryovers[].letter_grade` | string | No | Letter grade |
| `data.carryovers[].session` | string | No | Session name |
| `data.carryovers[].semester` | string | No | Semester name |
| `data.attendance_records` | array | No | Array of attendance records (max 20) |
| `data.attendance_records[].course` | string | No | Course code |
| `data.attendance_records[].course_title` | string | No | Course title |
| `data.attendance_records[].date` | string (ISO date) | No | Date |
| `data.attendance_records[].status` | string | No | Status |
| `data.attendance_records[].remarks` | string | Yes | Remarks |

**Error Responses:**

- **401 Unauthorized:** Not authenticated or wrong role
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **403 Forbidden:** Not a parent or not linked to student
```json
{
  "success": false,
  "error": "You are not authorized to view this student's information."
}
```

- **404 Not Found:** Parent profile or student not found
```json
{
  "success": false,
  "error": "Parent profile not found."
}
```
or
```json
{
  "success": false,
  "error": "Student not found."
}
```

- **500 Internal Server Error:** Server error
```json
{
  "success": false,
  "error": "An error occurred: <error message>"
}
```

**Frontend Rendering Recommendations:**
- Display student information in a header section
- Show academic summary with visual indicators
- Display results in a table with color coding
- Show carryovers in a separate section with warning styling
- Display attendance records in a table or calendar view
- Add back button to return to parent dashboard
- Cache data for 5 minutes (backend handles this)
- Implement tabs for results, carryovers, and attendance

---

## 6. CRUD API Reference

### 6.1 Students

**Base URL:** `/api/v1/students/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `grade_level`  
**Search Fields:** `student_id`, `user__username`, `user__first_name`, `user__last_name`  
**Ordering Fields:** `student_id`, `grade_level`, `enrollment_date`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Students (GET /api/v1/students/):**

```bash
curl -X GET "http://localhost:8000/api/v1/students/?grade_level=100&search=John" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/students/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "username": "student1",
        "email": "student1@school.edu",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student"
      },
      "student_id": "STU/2024/001",
      "date_of_birth": "2000-01-01",
      "grade_level": 100,
      "enrollment_date": "2024-01-15",
      "age": 24
    }
  ]
}
```

**Create Student (POST /api/v1/students/):**

```bash
curl -X POST http://localhost:8000/api/v1/students/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "student_id": "STU/2024/011",
    "date_of_birth": "2001-05-15",
    "grade_level": 100
  }'
```

**Retrieve Student (GET /api/v1/students/{id}/):**

```bash
curl -X GET http://localhost:8000/api/v1/students/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Update Student (PUT /api/v1/students/{id}/):**

```bash
curl -X PUT http://localhost:8000/api/v1/students/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU/2024/001",
    "date_of_birth": "2000-01-01",
    "grade_level": 200
  }'
```

**Delete Student (DELETE /api/v1/students/{id}/):**

```bash
curl -X DELETE http://localhost:8000/api/v1/students/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 6.2 Parents

**Base URL:** `/api/v1/parents/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Search Fields:** `user__username`, `user__first_name`, `user__last_name`, `occupation`  
**Ordering Fields:** `user__last_name`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Parents (GET /api/v1/parents/):**

```bash
curl -X GET "http://localhost:8000/api/v1/parents/?search=Richard" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 12,
        "username": "parent1",
        "email": "parent1@school.edu",
        "first_name": "Richard",
        "last_name": "Doe",
        "role": "parent"
      },
      "occupation": "Business Owner",
      "phone_number": "+12345678001"
    }
  ]
}
```

**Create Parent (POST /api/v1/parents/):**

```bash
curl -X POST http://localhost:8000/api/v1/parents/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 15,
    "occupation": "Teacher",
    "phone_number": "+12345678006"
  }'
```

**Retrieve Parent (GET /api/v1/parents/{id}/):**

```bash
curl -X GET http://localhost:8000/api/v1/parents/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Update Parent (PUT /api/v1/parents/{id}/):**

```bash
curl -X PUT http://localhost:8000/api/v1/parents/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "occupation": "Engineer",
    "phone_number": "+12345678099"
  }'
```

**Delete Parent (DELETE /api/v1/parents/{id}/):**

```bash
curl -X DELETE http://localhost:8000/api/v1/parents/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 6.3 Parent-Student Relations

**Base URL:** `/api/v1/parent-student-relations/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `relationship_type`  
**Search Fields:** `parent__user__username`, `parent__user__first_name`, `parent__user__last_name`, `student__user__username`, `student__user__first_name`, `student__user__last_name`, `student__student_id`  
**Ordering Fields:** `relationship_type`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Relations (GET /api/v1/parent-student-relations/):**

```bash
curl -X GET "http://localhost:8000/api/v1/parent-student-relations/?relationship_type=father" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "parent": {
        "id": 1,
        "user": {
          "id": 12,
          "username": "parent1",
          "email": "parent1@school.edu",
          "first_name": "Richard",
          "last_name": "Doe",
          "role": "parent"
        },
        "occupation": "Business Owner",
        "phone_number": "+12345678001"
      },
      "parent_id": 1,
      "student": {
        "id": 1,
        "user": {
          "id": 2,
          "username": "student1",
          "email": "student1@school.edu",
          "first_name": "John",
          "last_name": "Doe",
          "role": "student"
        },
        "student_id": "STU/2024/001",
        "date_of_birth": "2000-01-01",
        "grade_level": 100,
        "enrollment_date": "2024-01-15",
        "age": 24
      },
      "student_id": 1,
      "relationship_type": "father"
    }
  ]
}
```

**Create Relation (POST /api/v1/parent-student-relations/):**

```bash
curl -X POST http://localhost:8000/api/v1/parent-student-relations/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": 1,
    "student_id": 2,
    "relationship_type": "mother"
  }'
```

**Retrieve Relation (GET /api/v1/parent-student-relations/{id}/):**

```bash
curl -X GET http://localhost:8000/api/v1/parent-student-relations/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Update Relation (PUT /api/v1/parent-student-relations/{id}/):**

```bash
curl -X PUT http://localhost:8000/api/v1/parent-student-relations/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": 1,
    "student_id": 2,
    "relationship_type": "guardian"
  }'
```

**Delete Relation (DELETE /api/v1/parent-student-relations/{id}/):**

```bash
curl -X DELETE http://localhost:8000/api/v1/parent-student-relations/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 6.4 Academic Sessions

**Base URL:** `/api/v1/sessions/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `is_active`  
**Search Fields:** `name`  
**Ordering Fields:** `name`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Sessions (GET /api/v1/sessions/):**

```bash
curl -X GET "http://localhost:8000/api/v1/sessions/?is_active=true" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "2023/2024",
      "start_date": "2023-09-01",
      "end_date": "2024-07-31",
      "is_active": false,
      "is_active_display": "Inactive"
    },
    {
      "id": 2,
      "name": "2024/2025",
      "start_date": "2024-09-01",
      "end_date": "2025-07-31",
      "is_active": true,
      "is_active_display": "Active"
    }
  ]
}
```

**Create Session (POST /api/v1/sessions/):**

```bash
curl -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2025/2026",
    "start_date": "2025-09-01",
    "end_date": "2026-07-31",
    "is_active": false
  }'
```

---

### 6.5 Semesters

**Base URL:** `/api/v1/semesters/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `name`, `session`  
**Search Fields:** `name`, `session__name`  
**Ordering Fields:** `name`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Semesters (GET /api/v1/semesters/):**

```bash
curl -X GET "http://localhost:8000/api/v1/semesters/?session=2" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "first",
      "name_display": "First",
      "session": {
        "id": 2,
        "name": "2024/2025",
        "start_date": "2024-09-01",
        "end_date": "2025-07-31",
        "is_active": true,
        "is_active_display": "Active"
      },
      "session_id": 2
    },
    {
      "id": 2,
      "name": "second",
      "name_display": "Second",
      "session": {
        "id": 2,
        "name": "2024/2025",
        "start_date": "2024-09-01",
        "end_date": "2025-07-31",
        "is_active": true,
        "is_active_display": "Active"
      },
      "session_id": 2
    }
  ]
}
```

**Create Semester (POST /api/v1/semesters/):**

```bash
curl -X POST http://localhost:8000/api/v1/semesters/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "first",
    "session_id": 2
  }'
```

---

### 6.6 Levels

**Base URL:** `/api/v1/levels/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Search Fields:** `name`  
**Ordering Fields:** `name`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Levels (GET /api/v1/levels/):**

```bash
curl -X GET http://localhost:8000/api/v1/levels/ \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "100 Level"
    },
    {
      "id": 2,
      "name": "200 Level"
    },
    {
      "id": 3,
      "name": "300 Level"
    },
    {
      "id": 4,
      "name": "400 Level"
    },
    {
      "id": 5,
      "name": "500 Level"
    }
  ]
}
```

**Create Level (POST /api/v1/levels/):**

```bash
curl -X POST http://localhost:8000/api/v1/levels/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "600 Level"
  }'
```

---

### 6.7 Courses

**Base URL:** `/api/v1/courses/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `level`, `semester`, `credit_unit`, `is_active`  
**Search Fields:** `course_code`, `course_title`  
**Ordering Fields:** `course_code`, `course_title`, `credit_unit`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Courses (GET /api/v1/courses/):**

```bash
curl -X GET "http://localhost:8000/api/v1/courses/?level=1&is_active=true" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "course_code": "CSC101",
      "course_title": "Introduction to Computer Science",
      "credit_unit": 3,
      "level": {
        "id": 1,
        "name": "100 Level"
      },
      "level_id": 1,
      "semester": {
        "id": 1,
        "name": "first",
        "name_display": "First",
        "session": {
          "id": 2,
          "name": "2024/2025",
          "start_date": "2024-09-01",
          "end_date": "2025-07-31",
          "is_active": true,
          "is_active_display": "Active"
        },
        "session_id": 2
      },
      "semester_id": 1,
      "is_active": true
    }
  ]
}
```

**Create Course (POST /api/v1/courses/):**

```bash
curl -X POST http://localhost:8000/api/v1/courses/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "course_code": "CSC102",
    "course_title": "Programming Fundamentals",
    "credit_unit": 3,
    "level_id": 1,
    "semester_id": 2,
    "is_active": true
  }'
```

---

### 6.8 Student Enrollments

**Base URL:** `/api/v1/enrollments/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `session`, `level`  
**Search Fields:** `student__student_id`, `student__user__username`, `student__user__first_name`, `student__user__last_name`, `session__name`  
**Ordering Fields:** `enrollment_date`, `session__name`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Enrollments (GET /api/v1/enrollments/):**

```bash
curl -X GET "http://localhost:8000/api/v1/enrollments/?session=2" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "student": {
        "id": 1,
        "user": {
          "id": 2,
          "username": "student1",
          "email": "student1@school.edu",
          "first_name": "John",
          "last_name": "Doe",
          "role": "student"
        },
        "student_id": "STU/2024/001",
        "date_of_birth": "2000-01-01",
        "grade_level": 100,
        "enrollment_date": "2024-01-15",
        "age": 24
      },
      "student_id": 1,
      "session": {
        "id": 2,
        "name": "2024/2025",
        "start_date": "2024-09-01",
        "end_date": "2025-07-31",
        "is_active": true,
        "is_active_display": "Active"
      },
      "session_id": 2,
      "level": {
        "id": 1,
        "name": "100 Level"
      },
      "level_id": 1,
      "enrollment_date": "2024-01-15"
    }
  ]
}
```

**Create Enrollment (POST /api/v1/enrollments/):**

```bash
curl -X POST http://localhost:8000/api/v1/enrollments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "session_id": 2,
    "level_id": 1
  }'
```

---

### 6.9 Course Registrations

**Base URL:** `/api/v1/registrations/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `session`, `semester`, `is_carryover`  
**Search Fields:** `student__student_id`, `student__user__username`, `course__course_code`, `course__course_title`, `session__name`  
**Ordering Fields:** `registration_date`, `course__course_code`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Registrations (GET /api/v1/registrations/):**

```bash
curl -X GET "http://localhost:8000/api/v1/registrations/?session=2&is_carryover=false" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/registrations/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "student": {
        "id": 1,
        "user": {
          "id": 2,
          "username": "student1",
          "email": "student1@school.edu",
          "first_name": "John",
          "last_name": "Doe",
          "role": "student"
        },
        "student_id": "STU/2024/001",
        "date_of_birth": "2000-01-01",
        "grade_level": 100,
        "enrollment_date": "2024-01-15",
        "age": 24
      },
      "student_id": 1,
      "course": {
        "id": 1,
        "course_code": "CSC101",
        "course_title": "Introduction to Computer Science",
        "credit_unit": 3,
        "level": {
          "id": 1,
          "name": "100 Level"
        },
        "level_id": 1,
        "semester": {
          "id": 1,
          "name": "first",
          "name_display": "First",
          "session": {
            "id": 2,
            "name": "2024/2025",
            "start_date": "2024-09-01",
            "end_date": "2025-07-31",
            "is_active": true,
            "is_active_display": "Active"
          },
          "session_id": 2
        },
        "semester_id": 1,
        "is_active": true
      },
      "course_id": 1,
      "session": {
        "id": 2,
        "name": "2024/2025",
        "start_date": "2024-09-01",
        "end_date": "2025-07-31",
        "is_active": true,
        "is_active_display": "Active"
      },
      "session_id": 2,
      "semester": {
        "id": 1,
        "name": "first",
        "name_display": "First",
        "session": {
          "id": 2,
          "name": "2024/2025",
          "start_date": "2024-09-01",
          "end_date": "2025-07-31",
          "is_active": true,
          "is_active_display": "Active"
        },
        "session_id": 2
      },
      "semester_id": 1,
      "registration_date": "2024-01-15",
      "is_carryover": false,
      "is_carryover_display": "No"
    }
  ]
}
```

**Create Registration (POST /api/v1/registrations/):**

```bash
curl -X POST http://localhost:8000/api/v1/registrations/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 1,
    "session_id": 2,
    "semester_id": 1,
    "is_carryover": false
  }'
```

---

### 6.10 Grades

**Base URL:** `/api/v1/grades/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `letter_grade`, `grade_point`  
**Search Fields:** `registration__student__student_id`, `registration__student__user__username`, `registration__course__course_code`, `registration__course__course_title`, `registration__session__name`  
**Ordering Fields:** `updated_at`, `score`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Grades (GET /api/v1/grades/):**

```bash
curl -X GET "http://localhost:8000/api/v1/grades/?letter_grade=A" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "registration": {
        "id": 1,
        "student": {
          "id": 1,
          "user": {
            "id": 2,
            "username": "student1",
            "email": "student1@school.edu",
            "first_name": "John",
            "last_name": "Doe",
            "role": "student"
          },
          "student_id": "STU/2024/001",
          "date_of_birth": "2000-01-01",
          "grade_level": 100,
          "enrollment_date": "2024-01-15",
          "age": 24
        },
        "student_id": 1,
        "course": {
          "id": 1,
          "course_code": "CSC101",
          "course_title": "Introduction to Computer Science",
          "credit_unit": 3,
          "level": {
            "id": 1,
            "name": "100 Level"
          },
          "level_id": 1,
          "semester": {
            "id": 1,
            "name": "first",
            "name_display": "First",
            "session": {
              "id": 2,
              "name": "2024/2025",
              "start_date": "2024-09-01",
              "end_date": "2025-07-31",
              "is_active": true,
              "is_active_display": "Active"
            },
            "session_id": 2
          },
          "semester_id": 1,
          "is_active": true
        },
        "course_id": 1,
        "session": {
          "id": 2,
          "name": "2024/2025",
          "start_date": "2024-09-01",
          "end_date": "2025-07-31",
          "is_active": true,
          "is_active_display": "Active"
        },
        "session_id": 2,
        "semester": {
          "id": 1,
          "name": "first",
          "name_display": "First",
          "session": {
            "id": 2,
            "name": "2024/2025",
            "start_date": "2024-09-01",
            "end_date": "2025-07-31",
            "is_active": true,
            "is_active_display": "Active"
          },
          "session_id": 2
        },
        "semester_id": 1,
        "registration_date": "2024-01-15",
        "is_carryover": false,
        "is_carryover_display": "No"
      },
      "registration_id": 1,
      "score": 85.0,
      "letter_grade": "A",
      "grade_point": 5,
      "created_at": "2024-02-15T10:30:00Z",
      "updated_at": "2024-02-15T10:30:00Z"
    }
  ]
}
```

**Create Grade (POST /api/v1/grades/):**

```bash
curl -X POST http://localhost:8000/api/v1/grades/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "registration_id": 1,
    "score": 85.0
  }'
```

---

### 6.11 Attendance

**Base URL:** `/api/v1/attendance/`  
**Supported Methods:** GET, POST, PUT, PATCH, DELETE  
**Filters:** `status`, `date`  
**Search Fields:** `student__student_id`, `student__user__username`, `course__course_code`, `course__course_title`  
**Ordering Fields:** `date`, `status`  
**Pagination:** PageNumberPagination (default page size: 25)

**List Attendance (GET /api/v1/attendance/):**

```bash
curl -X GET "http://localhost:8000/api/v1/attendance/?status=present&date=2024-09-01" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/attendance/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "student": {
        "id": 1,
        "user": {
          "id": 2,
          "username": "student1",
          "email": "student1@school.edu",
          "first_name": "John",
          "last_name": "Doe",
          "role": "student"
        },
        "student_id": "STU/2024/001",
        "date_of_birth": "2000-01-01",
        "grade_level": 100,
        "enrollment_date": "2024-01-15",
        "age": 24
      },
      "student_id": 1,
      "course": {
        "id": 1,
        "course_code": "CSC101",
        "course_title": "Introduction to Computer Science",
        "credit_unit": 3,
        "level": {
          "id": 1,
          "name": "100 Level"
        },
        "level_id": 1,
        "semester": {
          "id": 1,
          "name": "first",
          "name_display": "First",
          "session": {
            "id": 2,
            "name": "2024/2025",
            "start_date": "2024-09-01",
            "end_date": "2025-07-31",
            "is_active": true,
            "is_active_display": "Active"
          },
          "session_id": 2
        },
        "semester_id": 1,
        "is_active": true
      },
      "course_id": 1,
      "date": "2024-09-01",
      "status": "present",
      "status_display": "Present",
      "created_at": "2024-09-01T08:00:00Z"
    }
  ]
}
```

**Create Attendance (POST /api/v1/attendance/):**

```bash
curl -X POST http://localhost:8000/api/v1/attendance/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 1,
    "date": "2024-09-01",
    "status": "present",
    "remarks": ""
  }'
```

---

## 7. TypeScript Interfaces

```typescript
// ============================================
// Common Response Types
// ============================================

interface SuccessResponse<T = any> {
  success: true;
  data: T;
  message?: string;
}

interface ErrorResponse {
  success: false;
  error: string;
  details?: Record<string, any>;
}

// ============================================
// Authentication Types
// ============================================

interface LoginRequest {
  email?: string;
  username?: string;
  password: string;
}

interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
  profile?: StudentProfile | ParentProfile | null;
}

interface RefreshTokenRequest {
  refresh: string;
}

interface RefreshTokenResponse {
  access: string;
}

interface LogoutRequest {
  refresh_token: string;
}

interface LogoutResponse {
  success: true;
  message: string;
}

interface CurrentUserResponse {
  success: true;
  data: UserWithProfile;
}

// ============================================
// User Types
// ============================================

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'student' | 'parent';
  is_active?: boolean;
  date_joined?: string;
  last_login?: string;
}

interface UserPublic {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'student' | 'parent';
}

interface UserWithProfile extends User {
  profile?: StudentProfile | ParentProfile | null;
}

// ============================================
// Student Profile Types
// ============================================

interface StudentProfile {
  id: number;
  user: UserPublic;
  user_id?: number;
  student_id: string;
  date_of_birth: string;
  grade_level: number;
  enrollment_date: string;
  age?: number;
}

interface StudentProfileDetail extends StudentProfile {
  user: User;
}

// ============================================
// Parent Profile Types
// ============================================

interface ParentProfile {
  id: number;
  user: UserPublic;
  user_id?: number;
  occupation: string;
  phone_number: string;
}

interface ParentProfileDetail extends ParentProfile {
  user: User;
}

// ============================================
// Parent-Student Relation Types
// ============================================

interface ParentStudentRelation {
  id: number;
  parent: ParentProfile;
  parent_id: number;
  student: StudentProfile;
  student_id: number;
  relationship_type: 'father' | 'mother' | 'guardian';
}

interface ParentStudentRelationDetail extends ParentStudentRelation {
  parent: ParentProfileDetail;
  student: StudentProfileDetail;
}

// ============================================
// Academic Session Types
// ============================================

interface AcademicSession {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  is_active_display: string;
}

// ============================================
// Semester Types
// ============================================

interface Semester {
  id: number;
  name: 'first' | 'second';
  name_display: string;
  session: AcademicSession;
  session_id: number;
}

// ============================================
// Level Types
// ============================================

interface Level {
  id: number;
  name: string;
}

// ============================================
// Course Types
// ============================================

interface Course {
  id: number;
  course_code: string;
  course_title: string;
  credit_unit: number;
  level: Level;
  level_id: number;
  semester: Semester;
  semester_id: number;
  is_active: boolean;
}

// ============================================
// Student Enrollment Types
// ============================================

interface StudentEnrollment {
  id: number;
  student: StudentProfile;
  student_id: number;
  session: AcademicSession;
  session_id: number;
  level: Level;
  level_id: number;
  enrollment_date: string;
}

// ============================================
// Course Registration Types
// ============================================

interface CourseRegistration {
  id: number;
  student: StudentProfile;
  student_id: number;
  course: Course;
  course_id: number;
  session: AcademicSession;
  session_id: number;
  semester: Semester;
  semester_id: number;
  registration_date: string;
  is_carryover: boolean;
  is_carryover_display: string;
}

interface CourseRegistrationDetail extends CourseRegistration {
  student: StudentProfileDetail;
}

// ============================================
// Grade Types
// ============================================

interface Grade {
  id: number;
  registration: CourseRegistration;
  registration_id: number;
  score: number;
  letter_grade: string;
  grade_point: number;
  created_at: string;
  updated_at: string;
}

interface GradeDetail extends Grade {
  registration: CourseRegistrationDetail;
}

// ============================================
// Attendance Types
// ============================================

interface Attendance {
  id: number;
  student: StudentProfile;
  student_id: number;
  course: Course;
  course_id: number;
  date: string;
  status: 'present' | 'absent';
  status_display: string;
  created_at: string;
}

interface AttendanceDetail extends Attendance {
  student: StudentProfileDetail;
}

// ============================================
// Student Dashboard Types
// ============================================

interface StudentInfo {
  name: string;
  matric_number: string;
  level: number;
}

interface RecentResult {
  course_code: string;
  course_title: string;
  score: number;
  grade: string;
  session: string;
  semester: string;
}

interface StudentDashboardData {
  student_info: StudentInfo;
  cgpa: number;
  academic_standing: string;
  attendance_percentage: number;
  carryover_count: number;
  total_courses_registered: number;
  recent_results: RecentResult[];
}

interface StudentDashboardResponse extends SuccessResponse<StudentDashboardData> {}

// ============================================
// Student Results Types
// ============================================

interface StudentResult {
  course_code: string;
  course_title: string;
  score: number;
  letter_grade: string;
  grade_point: number;
  session: string;
  semester: string;
  credit_unit: number;
}

interface StudentResultsResponse extends SuccessResponse<StudentResult[]> {}

// ============================================
// Student Attendance Types
// ============================================

interface AttendanceRecord {
  course: string;
  course_title: string;
  date: string;
  status: string;
  remarks?: string;
}

interface StudentAttendanceData {
  attendance_percentage: number;
  total_records: number;
  present_records: number;
  absent_records: number;
  records: AttendanceRecord[];
}

interface StudentAttendanceResponse extends SuccessResponse<StudentAttendanceData> {}

// ============================================
// Parent Dashboard Types
// ============================================

interface WardInfo {
  student_id: number;
  name: string;
  matric_number: string;
  level: number;
  cgpa: number;
  academic_standing: string;
  attendance_percentage: number;
  carryover_count: number;
  total_courses: number;
  relationship_type: string;
}

interface ParentDashboardData {
  parent_name: string;
  total_wards: number;
  wards: WardInfo[];
}

interface ParentDashboardResponse extends SuccessResponse<ParentDashboardData> {}

// ============================================
// Parent Ward Detail Types
// ============================================

interface WardDetailInfo {
  student_id: number;
  name: string;
  matric_number: string;
  level: number;
  email: string;
}

interface Carryover {
  course_code: string;
  course_title: string;
  score: number;
  letter_grade: string;
  session: string;
  semester: string;
}

interface ParentWardData {
  student_info: WardDetailInfo;
  cgpa: number;
  academic_standing: string;
  attendance_percentage: number;
  carryover_count: number;
  total_courses: number;
  relationship_type: string;
  results: StudentResult[];
  carryovers: Carryover[];
  attendance_records: AttendanceRecord[];
}

interface ParentWardResponse extends SuccessResponse<ParentWardData> {}

// ============================================
// Paginated Response Types
// ============================================

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ============================================
// ViewSet Response Types
// ============================================

interface StudentsListResponse extends PaginatedResponse<StudentProfile> {}
interface StudentsDetailResponse extends SuccessResponse<StudentProfileDetail> {}

interface ParentsListResponse extends PaginatedResponse<ParentProfile> {}
interface ParentsDetailResponse extends SuccessResponse<ParentProfileDetail> {}

interface ParentStudentRelationsListResponse extends PaginatedResponse<ParentStudentRelation> {}
interface ParentStudentRelationsDetailResponse extends SuccessResponse<ParentStudentRelationDetail> {}

interface SessionsListResponse extends PaginatedResponse<AcademicSession> {}
interface SemestersListResponse extends PaginatedResponse<Semester> {}
interface LevelsListResponse extends PaginatedResponse<Level> {}
interface CoursesListResponse extends PaginatedResponse<Course> {}

interface EnrollmentsListResponse extends PaginatedResponse<StudentEnrollment> {}
interface RegistrationsListResponse extends PaginatedResponse<CourseRegistration> {}
interface RegistrationsDetailResponse extends SuccessResponse<CourseRegistrationDetail> {}

interface GradesListResponse extends PaginatedResponse<Grade> {}
interface GradesDetailResponse extends SuccessResponse<GradeDetail> {}

interface AttendanceListResponse extends PaginatedResponse<Attendance> {}
interface AttendanceDetailResponse extends SuccessResponse<AttendanceDetail> {}
```

---

## 8. React Integration Guide

### 8.1 Axios Setup

Create an axios instance with base configuration:

```typescript
// src/lib/axios.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export default api;
```

### 8.2 JWT Interceptor Setup

Implement automatic token refresh and error handling:

```typescript
// src/lib/axios.ts (continued)
import { refreshAccessToken } from '@/lib/auth';

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
}> = [];

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      isRefreshing = true;
      originalRequest._retry = true;

      try {
        const newAccessToken = await refreshAccessToken();
        localStorage.setItem('access_token', newAccessToken);
        
        api.defaults.headers.Authorization = `Bearer ${newAccessToken}`;
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        
        failedQueue.forEach(({ resolve }) => resolve(newAccessToken));
        failedQueue = [];
        
        return api(originalRequest);
      } catch (refreshError) {
        failedQueue.forEach(({ reject }) => reject(refreshError));
        failedQueue = [];
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
```

### 8.3 Refresh Token Strategy

```typescript
// src/lib/auth.ts
import api from './axios';

export async function refreshAccessToken(): Promise<string> {
  const refreshToken = localStorage.getItem('refresh_token');
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  const response = await api.post('/auth/refresh/', {
    refresh: refreshToken,
  });

  const newAccessToken = response.data.access;
  
  // Update refresh token if rotation is enabled
  if (response.data.refresh) {
    localStorage.setItem('refresh_token', response.data.refresh);
  }

  return newAccessToken;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/auth/login/', {
    email,
    password,
  });

  localStorage.setItem('access_token', response.data.access);
  localStorage.setItem('refresh_token', response.data.refresh);

  return response.data;
}

export async function logout(): Promise<void> {
  const refreshToken = localStorage.getItem('refresh_token');
  
  try {
    await api.post('/auth/logout/', {
      refresh_token: refreshToken,
    });
  } catch (error) {
    // Ignore logout errors, just clear tokens
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export async function getCurrentUser(): Promise<UserWithProfile> {
  const response = await api.get<CurrentUserResponse>('/auth/me/');
  return response.data.data;
}
```

### 8.4 Protected Routes

Implement route guards using React Router:

```typescript
// src/components/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: ('admin' | 'student' | 'parent')[];
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
}
```

### 8.5 Role-Based Route Guards

```typescript
// src/hooks/useAuth.ts
import { useState, useEffect } from 'react';
import { getCurrentUser } from '@/lib/auth';

export function useAuth() {
  const [user, setUser] = useState<UserWithProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const userData = await getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      } finally {
        setLoading(false);
      }
    }

    fetchUser();
  }, []);

  const isAdmin = user?.role === 'admin';
  const isStudent = user?.role === 'student';
  const isParent = user?.role === 'parent';

  return { user, loading, isAdmin, isStudent, isParent };
}
```

### 8.6 Error Handling Strategy

```typescript
// src/lib/errorHandler.ts
import axios, { AxiosError } from 'axios';

export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    
    if (axiosError.response) {
      const { status, data } = axiosError.response;
      
      switch (status) {
        case 401:
          return 'Authentication required. Please log in.';
        case 403:
          return 'You do not have permission to perform this action.';
        case 404:
          return 'The requested resource was not found.';
        case 500:
          return 'Server error. Please try again later.';
        default:
          return data?.error || data?.detail || 'An error occurred.';
      }
    } else if (axiosError.request) {
      return 'Network error. Please check your connection.';
    }
  }
  
  return 'An unexpected error occurred.';
}

export function showErrorToast(message: string): void {
  // Implement your toast notification logic
  console.error(message);
}
```

### 8.7 Loading State Strategy

```typescript
// src/hooks/useApi.ts
import { useState, useEffect } from 'react';
import api from '@/lib/axios';

export function useApi<T>(url: string, options?: any) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const response = await api.get<T>(url, options);
        setData(response.data);
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [url, options]);

  return { data, loading, error, refetch: () => fetchData() };
}
```

---

## 9. Frontend Folder Structure Recommendation

```
school-monitoring-frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── app/                          # Next.js App Router (or pages for CRA)
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── (student)/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── results/
│   │   │   │   └── page.tsx
│   │   │   └── attendance/
│   │   │       └── page.tsx
│   │   ├── (parent)/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   └── wards/
│   │   │       └── [id]/
│   │   │           └── page.tsx
│   │   ├── (admin)/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── students/
│   │   │   │   └── page.tsx
│   │   │   ├── parents/
│   │   │   │   └── page.tsx
│   │   │   ├── courses/
│   │   │   │   └── page.tsx
│   │   │   └── grades/
│   │   │       └── page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── dashboard/
│   │   │   ├── StudentDashboard.tsx
│   │   │   ├── ParentDashboard.tsx
│   │   │   └── AdminDashboard.tsx
│   │   ├── academic/
│   │   │   ├── ResultsTable.tsx
│   │   │   ├── AttendanceCalendar.tsx
│   │   │   └── CGPACard.tsx
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   └── Modal.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── lib/
│   │   ├── axios.ts
│   │   ├── auth.ts
│   │   └── errorHandler.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── usePagination.ts
│   ├── context/
│   │   └── AuthContext.tsx
│   ├── types/
│   │   └── api.ts
│   ├── services/
│   │   ├── auth.service.ts
│   │   ├── student.service.ts
│   │   ├── parent.service.ts
│   │   └── admin.service.ts
│   └── utils/
│       ├── formatters.ts
│       └── validators.ts
├── .env.local
├── .gitignore
├── next.config.js
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

---

## 10. Frontend Readiness Assessment

### Stable Endpoints

All endpoints are stable and production-ready:

**Authentication:**
- ✅ POST /api/v1/auth/login/ - Supports both email and username login
- ✅ POST /api/v1/auth/refresh/ - Token refresh with rotation
- ✅ POST /api/v1/auth/logout/ - Token blacklisting
- ✅ GET /api/v1/auth/me/ - Current user information

**Student Dashboard:**
- ✅ GET /api/v1/student/dashboard/ - Comprehensive academic summary
- ✅ GET /api/v1/student/results/ - Grade records with filtering
- ✅ GET /api/v1/student/attendance/ - Attendance records with statistics

**Parent Dashboard:**
- ✅ GET /api/v1/parent/dashboard/ - Overview of linked students
- ✅ GET /api/v1/parent/wards/{id}/ - Detailed ward information

**CRUD ViewSets:**
- ✅ /api/v1/students/ - Full CRUD with RBAC
- ✅ /api/v1/parents/ - Full CRUD with RBAC
- ✅ /api/v1/parent-student-relations/ - Full CRUD with RBAC
- ✅ /api/v1/sessions/ - Full CRUD with RBAC
- ✅ /api/v1/semesters/ - Full CRUD with RBAC
- ✅ /api/v1/levels/ - Full CRUD with RBAC
- ✅ /api/v1/courses/ - Full CRUD with RBAC
- ✅ /api/v1/enrollments/ - Full CRUD with RBAC
- ✅ /api/v1/registrations/ - Full CRUD with RBAC
- ✅ /api/v1/grades/ - Full CRUD with RBAC
- ✅ /api/v1/attendance/ - Full CRUD with RBAC

### Required Endpoints

All required endpoints for frontend development are available and stable:
- ✅ Authentication flow (login, refresh, logout, current user)
- ✅ Role-based access control
- ✅ Student dashboard APIs
- ✅ Parent dashboard APIs
- ✅ CRUD operations for all resources
- ✅ Filtering, searching, and pagination
- ✅ Standardized response formats

### Optional Endpoints

No optional endpoints - all documented endpoints are fully functional.

### Missing Functionality

**None.** The backend is feature-complete for frontend development.

### Additional Notes

- **Caching:** Dashboard endpoints are cached for 5 minutes to improve performance
- **Pagination:** All list endpoints support pagination (default 25 items per page)
- **Filtering:** All ViewSets support filtering via query parameters
- **Searching:** All ViewSets support full-text search on relevant fields
- **Ordering:** All ViewSets support ordering on relevant fields
- **OpenAPI Documentation:** Full Swagger documentation available at `/api/schema/`
- **Standardized Responses:** All endpoints use consistent success/error response formats

### Frontend Development Status

**Status:** ✅ **FRONTEND READY**

The backend is fully stable and ready for frontend development. All endpoints are tested, documented, and follow consistent patterns. The API contract is complete with TypeScript interfaces provided for type safety.

---

## Appendix

### Environment Variables

Create a `.env.local` file in your frontend project:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Testing Credentials

For development and testing:

**Admin:**
- Email: admin@school.edu
- Username: admin
- Password: admin123

**Student:**
- Email: student1@school.edu
- Username: student1
- Password: student123

**Parent:**
- Email: parent1@school.edu
- Username: parent1
- Password: parent123

### OpenAPI Documentation

Access the full API documentation at:
- Swagger UI: `http://localhost:8000/api/schema/`
- OpenAPI Schema: `http://localhost:8000/api/schema/?format=json`

### Support

For API-related issues, refer to:
- Backend stability audit: Run `python manage.py stability_audit`
- API documentation: Access Swagger UI at `/api/schema/`
- Backend logs: Check Django development server logs

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-18  
**Backend Version:** Django 5.2+ with Django REST Framework  
**API Version:** v1
