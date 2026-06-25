"""
Unit tests for academic services.

Tests for GPA calculation, CGPA calculation, carryover detection,
and academic standing services.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from users.models import User, StudentProfile
from academics.models import (
    AcademicSession,
    Semester,
    Level,
    Course,
    CourseRegistration,
    Grade,
    Attendance,
)
from academics.services import (
    GPAService,
    AcademicStandingService,
    SemesterSummaryService,
    StudentDashboardService,
)


class AcademicServiceTestBase(TestCase):
    """Base test case with common setup for academic service tests."""
    
    def setUp(self):
        """Set up test data for academic service tests."""
        # Create user and student
        self.user = User.objects.create_user(
            username='teststudent',
            email='test@student.com',
            password='testpass123',
            role='student'
        )
        self.student = StudentProfile.objects.create(
            user=self.user,
            student_id='STU001',
            date_of_birth=date(2000, 1, 1),
            grade_level=100
        )
        
        # Create academic session
        self.session = AcademicSession.objects.create(
            name='2025/2026',
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
            is_active=True
        )
        
        # Create semesters
        self.first_semester = Semester.objects.create(
            name='first',
            session=self.session
        )
        self.second_semester = Semester.objects.create(
            name='second',
            session=self.session
        )
        
        # Create levels
        self.level_100 = Level.objects.create(name='100 Level')
        self.level_200 = Level.objects.create(name='200 Level')
        
        # Create courses
        self.course1 = Course.objects.create(
            course_code='CSC101',
            course_title='Introduction to Computer Science',
            credit_unit=3,
            level=self.level_100,
            semester=self.first_semester
        )
        self.course2 = Course.objects.create(
            course_code='MTH101',
            course_title='Mathematics I',
            credit_unit=4,
            level=self.level_100,
            semester=self.first_semester
        )
        self.course3 = Course.objects.create(
            course_code='PHY101',
            course_title='Physics I',
            credit_unit=3,
            level=self.level_100,
            semester=self.first_semester
        )
        self.course4 = Course.objects.create(
            course_code='CSC102',
            course_title='Programming I',
            credit_unit=3,
            level=self.level_100,
            semester=self.second_semester
        )


class GPAServiceTests(AcademicServiceTestBase):
    """Test cases for GPAService."""
    
    def test_calculate_gpa_with_grades(self):
        """Test GPA calculation with valid grades."""
        # Register courses
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course2,
            session=self.session,
            semester=self.first_semester
        )
        
        # Create grades: A(5) in 3-unit course, B(4) in 4-unit course
        Grade.objects.create(registration=reg1, score=75)  # A = 5
        Grade.objects.create(registration=reg2, score=65)  # B = 4
        
        # Calculate GPA
        result = GPAService.calculate_gpa(self.student, self.session, self.first_semester)
        
        # Expected: (5*3 + 4*4) / (3+4) = (15 + 16) / 7 = 31/7 = 4.43
        self.assertEqual(result['gpa'], 4.43)
        self.assertEqual(result['total_credit_units'], 7)
        self.assertEqual(result['total_quality_points'], 31.0)
    
    def test_calculate_gpa_no_grades(self):
        """Test GPA calculation when no grades exist."""
        result = GPAService.calculate_gpa(self.student, self.session, self.first_semester)
        
        self.assertEqual(result['gpa'], 0.0)
        self.assertEqual(result['total_credit_units'], 0)
        self.assertEqual(result['total_quality_points'], 0)
    
    def test_calculate_gpa_with_failures(self):
        """Test GPA calculation with failed courses."""
        # Register course
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        
        # Create grade: F(0) in 3-unit course
        Grade.objects.create(registration=reg1, score=35)  # F = 0
        
        result = GPAService.calculate_gpa(self.student, self.session, self.first_semester)
        
        # Expected: (0*3) / 3 = 0
        self.assertEqual(result['gpa'], 0.0)
        self.assertEqual(result['total_credit_units'], 3)
        self.assertEqual(result['total_quality_points'], 0)
    
    def test_calculate_gpa_invalid_input(self):
        """Test GPA calculation with invalid input."""
        with self.assertRaises(ValueError):
            GPAService.calculate_gpa(None, self.session, self.first_semester)
        
        with self.assertRaises(ValueError):
            GPAService.calculate_gpa(self.student, None, self.first_semester)
        
        with self.assertRaises(ValueError):
            GPAService.calculate_gpa(self.student, self.session, None)
    
    def test_calculate_cgpa(self):
        """Test CGPA calculation across multiple semesters."""
        # First semester courses
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course2,
            session=self.session,
            semester=self.first_semester
        )
        
        # Second semester courses
        reg4 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course4,
            session=self.session,
            semester=self.second_semester
        )
        
        # Create grades
        Grade.objects.create(registration=reg1, score=75)  # A=5, 3 units
        Grade.objects.create(registration=reg2, score=65)  # B=4, 4 units
        Grade.objects.create(registration=reg4, score=55)  # C=3, 3 units
        
        result = GPAService.calculate_cgpa(self.student)
        
        # Expected: (5*3 + 4*4 + 3*3) / (3+4+3) = (15+16+9) / 10 = 40/10 = 4.0
        self.assertEqual(result['cgpa'], 4.0)
        self.assertEqual(result['total_units'], 10)
        self.assertEqual(result['total_quality_points'], 40.0)
    
    def test_calculate_cgpa_no_grades(self):
        """Test CGPA calculation when no grades exist."""
        result = GPAService.calculate_cgpa(self.student)
        
        self.assertEqual(result['cgpa'], 0.0)
        self.assertEqual(result['total_units'], 0)
        self.assertEqual(result['total_quality_points'], 0)
    
    def test_get_carryover_courses(self):
        """Test carryover course detection."""
        # Register courses
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course2,
            session=self.session,
            semester=self.first_semester
        )
        
        # Create grades: one pass, one fail
        Grade.objects.create(registration=reg1, score=75)  # A=5
        Grade.objects.create(registration=reg2, score=35)  # F=0
        
        carryovers = GPAService.get_carryover_courses(self.student)
        
        self.assertEqual(carryovers.count(), 1)
        self.assertEqual(carryovers.first().registration.course.course_code, 'MTH101')
    
    def test_get_carryover_courses_by_letter_grade(self):
        """Test carryover detection by letter grade F."""
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        
        # Create grade with letter grade F
        grade = Grade.objects.create(registration=reg1, score=35)
        
        carryovers = GPAService.get_carryover_courses(self.student)
        
        self.assertEqual(carryovers.count(), 1)
        self.assertEqual(carryovers.first().letter_grade, 'F')
    
    def test_get_carryover_courses_no_failures(self):
        """Test carryover detection when no courses failed."""
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        
        Grade.objects.create(registration=reg1, score=75)
        
        carryovers = GPAService.get_carryover_courses(self.student)
        
        self.assertEqual(carryovers.count(), 0)


class AcademicStandingServiceTests(AcademicServiceTestBase):
    """Test cases for AcademicStandingService."""
    
    def test_excellent_standing(self):
        """Test excellent standing (CGPA >= 4.50)."""
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg1, score=85)  # A=5, 3 units
        
        result = AcademicStandingService.get_academic_standing(self.student)
        
        self.assertEqual(result['standing'], 'Excellent')
        self.assertGreaterEqual(result['cgpa'], 4.50)
    
    def test_good_standing(self):
        """Test good standing (CGPA >= 3.50)."""
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg1, score=65)  # B=4, 3 units
        
        result = AcademicStandingService.get_academic_standing(self.student)
        
        self.assertEqual(result['standing'], 'Good Standing')
        self.assertGreaterEqual(result['cgpa'], 3.50)
    
    def test_average_standing(self):
        """Test average standing (CGPA >= 2.40)."""
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg1, score=55)  # C=3, 3 units
        
        result = AcademicStandingService.get_academic_standing(self.student)
        
        self.assertEqual(result['standing'], 'Average Standing')
        self.assertGreaterEqual(result['cgpa'], 2.40)
    
    def test_probation_standing(self):
        """Test probation standing (CGPA >= 1.50)."""
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg1, score=45)  # D=2, 3 units
        
        result = AcademicStandingService.get_academic_standing(self.student)
        
        self.assertEqual(result['standing'], 'Probation')
        self.assertGreaterEqual(result['cgpa'], 1.50)
    
    def test_withdrawal_risk_standing(self):
        """Test withdrawal risk standing (CGPA < 1.50)."""
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg1, score=35)  # F=0, 3 units
        
        result = AcademicStandingService.get_academic_standing(self.student)
        
        self.assertEqual(result['standing'], 'Withdrawal Risk')
        self.assertLess(result['cgpa'], 1.50)
    
    def test_academic_standing_invalid_input(self):
        """Test academic standing with invalid input."""
        with self.assertRaises(ValueError):
            AcademicStandingService.get_academic_standing(None)


class SemesterSummaryServiceTests(AcademicServiceTestBase):
    """Test cases for SemesterSummaryService."""
    
    def test_semester_summary(self):
        """Test comprehensive semester summary."""
        # Register courses
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course2,
            session=self.session,
            semester=self.first_semester
        )
        
        # Create grades
        Grade.objects.create(registration=reg1, score=75)  # A=5
        Grade.objects.create(registration=reg2, score=35)  # F=0
        
        # Create attendance records
        Attendance.objects.create(
            student=self.student,
            course=self.course1,
            date=date(2025, 9, 15),
            status='present'
        )
        Attendance.objects.create(
            student=self.student,
            course=self.course1,
            date=date(2025, 9, 16),
            status='present'
        )
        Attendance.objects.create(
            student=self.student,
            course=self.course1,
            date=date(2025, 9, 17),
            status='absent'
        )
        
        result = SemesterSummaryService.get_semester_summary(
            self.student, self.session, self.first_semester
        )
        
        self.assertEqual(result['courses_taken'], 2)
        self.assertEqual(result['courses_passed'], 1)
        self.assertEqual(result['courses_failed'], 1)
        self.assertEqual(result['attendance_percentage'], 66.67)  # 2/3 * 100
    
    def test_semester_summary_no_attendance(self):
        """Test semester summary with no attendance records."""
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg1, score=75)
        
        result = SemesterSummaryService.get_semester_summary(
            self.student, self.session, self.first_semester
        )
        
        self.assertEqual(result['attendance_percentage'], 0.0)
    
    def test_semester_summary_invalid_input(self):
        """Test semester summary with invalid input."""
        with self.assertRaises(ValueError):
            SemesterSummaryService.get_semester_summary(None, self.session, self.first_semester)
        
        with self.assertRaises(ValueError):
            SemesterSummaryService.get_semester_summary(self.student, None, self.first_semester)
        
        with self.assertRaises(ValueError):
            SemesterSummaryService.get_semester_summary(self.student, self.session, None)


class StudentDashboardServiceTests(AcademicServiceTestBase):
    """Test cases for StudentDashboardService."""
    
    def test_student_dashboard(self):
        """Test comprehensive student dashboard."""
        # Register courses
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course2,
            session=self.session,
            semester=self.first_semester
        )
        
        # Create grades
        Grade.objects.create(registration=reg1, score=75)  # A=5
        Grade.objects.create(registration=reg2, score=35)  # F=0
        
        # Create attendance
        Attendance.objects.create(
            student=self.student,
            course=self.course1,
            date=date(2025, 9, 15),
            status='present'
        )
        
        result = StudentDashboardService.get_student_dashboard(self.student)
        
        self.assertIn('cgpa', result)
        self.assertIn('standing', result)
        self.assertIn('carryover_count', result)
        self.assertIn('total_courses', result)
        self.assertIn('attendance_percentage', result)
        
        self.assertEqual(result['carryover_count'], 1)
        self.assertEqual(result['total_courses'], 2)
        self.assertEqual(result['attendance_percentage'], 100.0)
    
    def test_student_dashboard_invalid_input(self):
        """Test student dashboard with invalid input."""
        with self.assertRaises(ValueError):
            StudentDashboardService.get_student_dashboard(None)
    
    def test_student_dashboard_no_data(self):
        """Test student dashboard with no academic data."""
        result = StudentDashboardService.get_student_dashboard(self.student)
        
        self.assertEqual(result['cgpa'], 0.0)
        self.assertEqual(result['carryover_count'], 0)
        self.assertEqual(result['total_courses'], 0)
        self.assertEqual(result['attendance_percentage'], 0.0)


class CourseRetakeTests(AcademicServiceTestBase):
    """Test cases for course retake scenarios."""
    
    def test_course_retake_after_failure(self):
        """Test that a student can retake a failed course in a different session."""
        # Create a second session
        session2 = AcademicSession.objects.create(
            name='2026/2027',
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 31),
            is_active=False
        )
        
        # First attempt - fail the course
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester,
            is_carryover=False
        )
        grade1 = Grade.objects.create(registration=reg1, score=35)  # F=0
        
        # Second attempt - retake and pass
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=session2,
            semester=self.first_semester,
            is_carryover=True
        )
        grade2 = Grade.objects.create(registration=reg2, score=75)  # A=5
        
        # Both grades should exist
        self.assertEqual(Grade.objects.filter(registration__student=self.student).count(), 2)
        
        # CGPA should calculate correctly using both attempts
        result = GPAService.calculate_cgpa(self.student)
        # (0*3 + 5*3) / (3+3) = 15/6 = 2.5
        self.assertEqual(result['cgpa'], 2.5)
        self.assertEqual(result['total_units'], 6)
    
    def test_carryover_detection_after_retake(self):
        """Test carryover detection correctly identifies failed attempt."""
        # Create a second session
        session2 = AcademicSession.objects.create(
            name='2026/2027',
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 31),
            is_active=False
        )
        
        # First attempt - fail
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg1, score=35)  # F=0
        
        # Second attempt - pass
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=session2,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg2, score=75)  # A=5
        
        # Carryover detection should find the failed attempt
        carryovers = GPAService.get_carryover_courses(self.student)
        self.assertEqual(carryovers.count(), 1)
        self.assertEqual(carryovers.first().registration.session.name, '2025/2026')
    
    def test_gpa_calculation_with_multiple_attempts(self):
        """Test GPA calculation uses only the specified session/semester."""
        # Create a second session
        session2 = AcademicSession.objects.create(
            name='2026/2027',
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 31),
            is_active=False
        )
        
        # First session - fail
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg1, score=35)  # F=0
        
        # Second session - pass
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=session2,
            semester=self.first_semester
        )
        Grade.objects.create(registration=reg2, score=75)  # A=5
        
        # GPA for first session should only include first attempt
        result1 = GPAService.calculate_gpa(self.student, self.session, self.first_semester)
        self.assertEqual(result1['gpa'], 0.0)
        
        # GPA for second session should only include second attempt
        result2 = GPAService.calculate_gpa(self.student, session2, self.first_semester)
        self.assertEqual(result2['gpa'], 5.0)
    
    def test_academic_history_preservation(self):
        """Test that academic history is preserved across multiple attempts."""
        # Create multiple sessions
        session2 = AcademicSession.objects.create(
            name='2026/2027',
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 31),
            is_active=False
        )
        
        # First attempt
        reg1 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=self.session,
            semester=self.first_semester
        )
        grade1 = Grade.objects.create(registration=reg1, score=35)
        
        # Second attempt
        reg2 = CourseRegistration.objects.create(
            student=self.student,
            course=self.course1,
            session=session2,
            semester=self.first_semester
        )
        grade2 = Grade.objects.create(registration=reg2, score=75)
        
        # Both grades should be accessible
        all_grades = Grade.objects.filter(registration__student=self.student)
        self.assertEqual(all_grades.count(), 2)
        
        # Verify each grade has correct properties
        self.assertEqual(grade1.score, 35)
        self.assertEqual(grade1.letter_grade, 'F')
        self.assertEqual(grade1.registration.session.name, '2025/2026')
        
        self.assertEqual(grade2.score, 75)
        self.assertEqual(grade2.letter_grade, 'A')
        self.assertEqual(grade2.registration.session.name, '2026/2027')
