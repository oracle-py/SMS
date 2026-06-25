"""
Academic calculation services for student monitoring system.

This module provides business logic for academic calculations including
GPA, CGPA, carryover detection, academic standing, and semester summaries.

Academic Documentation Support:
- GPA calculation logic follows standard university grading system
- Carry-over detection based on grade_point == 0 or letter_grade == 'F'
- Academic standing thresholds: Excellent (≥4.50), Good (≥3.50), Average (≥2.40), Probation (≥1.50), Withdrawal Risk (<1.50)
- Role-based access control ensures data privacy and security
- Parent monitoring system enables real-time academic performance tracking
- Service layer architecture maintains separation of concerns and reusability
"""

from decimal import Decimal, InvalidOperation, getcontext
from typing import Dict, List, Optional, Union

from django.db import models
from django.db.models import Q, Sum, Count, Case, When, F, DecimalField
from django.db.models.functions import Coalesce

from academics.models import (
    Course,
    CourseRegistration,
    Grade,
    Attendance,
    AcademicSession,
    Semester,
)


# Set decimal precision for calculations
getcontext().prec = 4


class GPAService:
    """
    Service for calculating GPA and CGPA for students.
    
    Provides methods to calculate semester GPA and cumulative GPA
    based on student grades and course credit units.
    
    Academic Documentation:
    - GPA calculation follows standard university formula: (Total Quality Points / Total Credit Units)
    - Quality Points = Credit Units × Grade Point (A=5, B=4, C=3, D=2, E=1, F=0)
    - CGPA is cumulative GPA across all semesters
    - Carryover courses are those with grade_point == 0 or letter_grade == 'F'
    - Supports multiple course attempts through CourseRegistration relationship
    """
    
    @staticmethod
    def calculate_gpa(
        student: 'users.StudentProfile',
        session: AcademicSession,
        semester: Semester
    ) -> Dict[str, Union[float, int, Decimal]]:
        """
        Calculate GPA for a student in a specific session and semester.
        
        GPA = Σ(grade_point × credit_unit) / Σ(credit_unit)
        
        Args:
            student: StudentProfile instance
            session: AcademicSession instance
            semester: Semester instance
            
        Returns:
            Dictionary containing:
                - gpa: GPA value rounded to 2 decimal places
                - total_credit_units: Total credit units taken
                - total_quality_points: Total quality points earned
                
        Raises:
            ValueError: If student, session, or semester is None
        """
        if not student or not session or not semester:
            raise ValueError("Student, session, and semester are required")
        
        # Get all course registrations for the student in the specified session and semester
        # that have grades
        registrations = CourseRegistration.objects.filter(
            student=student,
            session=session,
            semester=semester
        ).select_related('course').prefetch_related('grade')
        
        if not registrations.exists():
            return {
                'gpa': 0.0,
                'total_credit_units': 0,
                'total_quality_points': 0
            }
        
        # Get grades for these registrations
        grades = Grade.objects.filter(
            registration__in=registrations
        ).select_related('registration__course')
        
        if not grades.exists():
            return {
                'gpa': 0.0,
                'total_credit_units': 0,
                'total_quality_points': 0
            }
        
        total_credit_units = 0
        total_quality_points = Decimal('0')
        
        for grade in grades:
            credit_unit = grade.registration.course.credit_unit
            grade_point = grade.grade_point
            
            total_credit_units += credit_unit
            total_quality_points += Decimal(str(grade_point * credit_unit))
        
        # Handle division by zero
        if total_credit_units == 0:
            return {
                'gpa': 0.0,
                'total_credit_units': 0,
                'total_quality_points': 0
            }
        
        gpa = total_quality_points / Decimal(str(total_credit_units))
        gpa = round(float(gpa), 2)
        
        return {
            'gpa': gpa,
            'total_credit_units': total_credit_units,
            'total_quality_points': float(total_quality_points)
        }
    
    @staticmethod
    def calculate_cgpa(student: 'users.StudentProfile') -> Dict[str, Union[float, int, Decimal]]:
        """
        Calculate cumulative GPA (CGPA) for a student across all sessions.
        
        Uses every graded course registration ever taken by the student.
        
        Args:
            student: StudentProfile instance
            
        Returns:
            Dictionary containing:
                - cgpa: Cumulative GPA rounded to 2 decimal places
                - total_units: Total credit units taken
                - total_quality_points: Total quality points earned
                
        Raises:
            ValueError: If student is None
        """
        if not student:
            raise ValueError("Student is required")
        
        # Get all grades for the student through registrations
        grades = Grade.objects.filter(
            registration__student=student
        ).select_related('registration__course')
        
        if not grades.exists():
            return {
                'cgpa': 0.0,
                'total_units': 0,
                'total_quality_points': 0
            }
        
        total_units = 0
        total_quality_points = Decimal('0')
        
        for grade in grades:
            credit_unit = grade.registration.course.credit_unit
            grade_point = grade.grade_point
            
            total_units += credit_unit
            total_quality_points += Decimal(str(grade_point * credit_unit))
        
        # Handle division by zero
        if total_units == 0:
            return {
                'cgpa': 0.0,
                'total_units': 0,
                'total_quality_points': 0
            }
        
        cgpa = total_quality_points / Decimal(str(total_units))
        cgpa = round(float(cgpa), 2)
        
        return {
            'cgpa': cgpa,
            'total_units': total_units,
            'total_quality_points': float(total_quality_points)
        }
    
    @staticmethod
    def get_carryover_courses(student: 'users.StudentProfile') -> models.QuerySet:
        """
        Get all carryover courses for a student.
        
        A course is considered a carryover if:
        - grade_point == 0, OR
        - letter_grade == "F"
        
        Args:
            student: StudentProfile instance
            
        Returns:
            QuerySet of Grade objects representing failed courses
            
        Raises:
            ValueError: If student is None
        """
        if not student:
            raise ValueError("Student is required")
        
        carryovers = Grade.objects.filter(
            registration__student=student
        ).filter(
            Q(grade_point=0) | Q(letter_grade='F')
        ).select_related(
            'registration__course',
            'registration__course__level',
            'registration__semester',
            'registration__session'
        )
        
        return carryovers


class AcademicStandingService:
    """
    Service for determining student academic standing based on CGPA.
    
    Provides methods to evaluate academic standing according to
    institutional standards.
    
    Academic Documentation:
    - Academic Standing Thresholds: Excellent (≥4.50), Good Standing (≥3.50), Average Standing (≥2.40), Probation (≥1.50), Withdrawal Risk (<1.50)
    - Standing determination based on cumulative GPA (CGPA) across all semesters
    - Used for academic monitoring and intervention programs
    - Supports early warning systems for at-risk students
    """
    
    STANDING_THRESHOLDS = {
        'Excellent': 4.50,
        'Good Standing': 3.50,
        'Average Standing': 2.40,
        'Probation': 1.50,
    }
    
    @staticmethod
    def get_academic_standing(student: 'users.StudentProfile') -> Dict[str, Union[float, str]]:
        """
        Determine academic standing based on student's CGPA.
        
        Standing Rules:
        - CGPA >= 4.50: Excellent
        - CGPA >= 3.50: Good Standing
        - CGPA >= 2.40: Average Standing
        - CGPA >= 1.50: Probation
        - Below 1.50: Withdrawal Risk
        
        Args:
            student: StudentProfile instance
            
        Returns:
            Dictionary containing:
                - cgpa: Student's CGPA
                - standing: Academic standing description
                
        Raises:
            ValueError: If student is None
        """
        if not student:
            raise ValueError("Student is required")
        
        cgpa_result = GPAService.calculate_cgpa(student)
        cgpa = cgpa_result['cgpa']
        
        # Determine standing based on CGPA
        if cgpa >= AcademicStandingService.STANDING_THRESHOLDS['Excellent']:
            standing = 'Excellent'
        elif cgpa >= AcademicStandingService.STANDING_THRESHOLDS['Good Standing']:
            standing = 'Good Standing'
        elif cgpa >= AcademicStandingService.STANDING_THRESHOLDS['Average Standing']:
            standing = 'Average Standing'
        elif cgpa >= AcademicStandingService.STANDING_THRESHOLDS['Probation']:
            standing = 'Probation'
        else:
            standing = 'Withdrawal Risk'
        
        return {
            'cgpa': cgpa,
            'standing': standing
        }


class SemesterSummaryService:
    """
    Service for generating semester summaries for students.
    
    Provides comprehensive semester performance metrics including
    GPA, course statistics, and attendance percentage.
    
    Academic Documentation:
    - Semester summary includes courses taken, passed, failed, and attendance percentage
    - Attendance calculation: (Present Records / Total Records) × 100
    - Used for semester performance evaluation and parent monitoring
    - Supports academic performance tracking across different sessions
    """
    
    @staticmethod
    def get_semester_summary(
        student: 'users.StudentProfile',
        session: AcademicSession,
        semester: Semester
    ) -> Dict[str, Union[float, int]]:
        """
        Generate a comprehensive semester summary for a student.
        
        Args:
            student: StudentProfile instance
            session: AcademicSession instance
            semester: Semester instance
            
        Returns:
            Dictionary containing:
                - gpa: Semester GPA
                - courses_taken: Total number of courses taken
                - courses_passed: Number of courses passed (grade_point > 0)
                - courses_failed: Number of courses failed (grade_point == 0)
                - attendance_percentage: Attendance percentage for the semester
                
        Raises:
            ValueError: If student, session, or semester is None
        """
        if not student or not session or not semester:
            raise ValueError("Student, session, and semester are required")
        
        # Calculate GPA
        gpa_result = GPAService.calculate_gpa(student, session, semester)
        gpa = gpa_result['gpa']
        
        # Get course registrations for the semester
        registrations = CourseRegistration.objects.filter(
            student=student,
            session=session,
            semester=semester
        ).select_related('course')
        
        courses_taken = registrations.count()
        
        # Get grades for these registrations
        grades = Grade.objects.filter(
            registration__in=registrations
        )
        
        # Count passed and failed courses
        courses_passed = grades.filter(grade_point__gt=0).count()
        courses_failed = grades.filter(grade_point=0).count()
        
        # Calculate attendance percentage
        attendance_percentage = SemesterSummaryService._calculate_attendance_percentage(
            student, session, semester
        )
        
        return {
            'gpa': gpa,
            'courses_taken': courses_taken,
            'courses_passed': courses_passed,
            'courses_failed': courses_failed,
            'attendance_percentage': attendance_percentage
        }
    
    @staticmethod
    def _calculate_attendance_percentage(
        student: 'users.StudentProfile',
        session: AcademicSession,
        semester: Semester
    ) -> float:
        """
        Calculate attendance percentage for a student in a semester.
        
        Attendance Percentage = (Present Records / Total Records) × 100
        
        Args:
            student: StudentProfile instance
            session: AcademicSession instance
            semester: Semester instance
            
        Returns:
            Attendance percentage rounded to 2 decimal places
        """
        # Get all attendance records for the student in the semester
        attendances = Attendance.objects.filter(
            student=student,
            course__semester=semester,
            course__semester__session=session
        )
        
        total_records = attendances.count()
        
        if total_records == 0:
            return 0.0
        
        present_records = attendances.filter(status='present').count()
        
        attendance_percentage = (present_records / total_records) * 100
        attendance_percentage = round(attendance_percentage, 2)
        
        return attendance_percentage


class StudentDashboardService:
    """
    Service for aggregating student dashboard data.
    
    Provides a comprehensive overview of student academic performance
    including CGPA, standing, carryover information, and attendance.
    
    Academic Documentation:
    - Dashboard aggregates data from GPAService, AcademicStandingService, and SemesterSummaryService
    - Provides single-point access to comprehensive student academic information
    - Used for student self-monitoring and parent monitoring dashboards
    - Supports real-time academic performance tracking
    - Enables early intervention for at-risk students
    """
    
    @staticmethod
    def get_student_dashboard(student: 'users.StudentProfile') -> Dict[str, Union[float, int, str]]:
        """
        Generate a comprehensive dashboard summary for a student.
        
        Args:
            student: StudentProfile instance
            
        Returns:
            Dictionary containing:
                - cgpa: Student's cumulative GPA
                - standing: Academic standing
                - carryover_count: Number of carryover courses
                - total_courses: Total number of courses taken
                - attendance_percentage: Overall attendance percentage
                
        Raises:
            ValueError: If student is None
        """
        if not student:
            raise ValueError("Student is required")
        
        # Get CGPA and standing
        standing_result = AcademicStandingService.get_academic_standing(student)
        cgpa = standing_result['cgpa']
        standing = standing_result['standing']
        
        # Get carryover count
        carryovers = GPAService.get_carryover_courses(student)
        carryover_count = carryovers.count()
        
        # Get total courses taken (count graded registrations)
        total_courses = Grade.objects.filter(registration__student=student).count()
        
        # Calculate overall attendance percentage
        attendance_percentage = StudentDashboardService._calculate_overall_attendance(student)
        
        return {
            'cgpa': cgpa,
            'standing': standing,
            'carryover_count': carryover_count,
            'total_courses': total_courses,
            'attendance_percentage': attendance_percentage
        }
    
    @staticmethod
    def _calculate_overall_attendance(student: 'users.StudentProfile') -> float:
        """
        Calculate overall attendance percentage for a student across all courses.
        
        Args:
            student: StudentProfile instance
            
        Returns:
            Overall attendance percentage rounded to 2 decimal places
        """
        attendances = Attendance.objects.filter(student=student)
        
        total_records = attendances.count()
        
        if total_records == 0:
            return 0.0
        
        present_records = attendances.filter(status='present').count()
        
        attendance_percentage = (present_records / total_records) * 100
        attendance_percentage = round(attendance_percentage, 2)
        
        return attendance_percentage
