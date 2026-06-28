"""
Django management command to seed demo data for the Student Monitoring System.

This command generates realistic academic data including:
- Admin user
- Students with varying academic performance
- Parents linked to students
- Academic sessions, semesters, levels, courses
- Enrollments, course registrations, grades, and attendance
"""

import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from users.models import User, StudentProfile, ParentProfile, ParentStudentRelation, LecturerProfile
from academics.models import (
    AcademicSession,
    Semester,
    Level,
    Course,
    StudentEnrollment,
    CourseRegistration,
    Grade,
    Attendance,
)


class Command(BaseCommand):
    """
    Management command to seed demo data for the Student Monitoring System.
    
    Generates realistic academic data with varying student performance levels
    including high performers, average students, and those on probation.
    """
    
    help = 'Seed demo data for the Student Monitoring System'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--flush',
            action='store_true',
            dest='flush',
            help='Delete existing demo data before reseeding',
        )
    
    def handle(self, *args, **options):
        """Execute the seed command."""
        flush = options.get('flush', False)

        # Always flush on production to ensure clean state
        if not flush:
            self.stdout.write(self.style.WARNING('Auto-flushing existing demo data for clean deployment...'))
            self.flush_demo_data()
        
        self.stdout.write(self.style.SUCCESS('Starting demo data seeding...'))
        
        try:
            with transaction.atomic():
                self.seed_users()
                self.seed_academic_structure()
                self.seed_enrollments_and_grades()
                self.seed_attendance()
                
            self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
            self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
            self.stdout.write(self.style.SUCCESS('Admin: admin / admin123'))
            self.stdout.write(self.style.SUCCESS('Student: student1 / student123'))
            self.stdout.write(self.style.SUCCESS('Parent: parent1 / parent123'))
            self.stdout.write(self.style.SUCCESS('Lecturer: lecturer1 / lecturer123'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
            raise
    
    def flush_demo_data(self):
        """Delete all demo data created by this command."""
        self.stdout.write('Deleting demo data...')
        
        # Delete in reverse order of creation to avoid foreign key violations
        Attendance.objects.all().delete()
        Grade.objects.all().delete()
        CourseRegistration.objects.all().delete()
        StudentEnrollment.objects.all().delete()
        Course.objects.all().delete()
        Semester.objects.all().delete()
        AcademicSession.objects.all().delete()
        Level.objects.all().delete()
        ParentStudentRelation.objects.all().delete()
        ParentProfile.objects.all().delete()
        StudentProfile.objects.all().delete()
        
        # Delete demo users (admin, student1-10, parent1-5, lecturer1-5)
        User.objects.filter(username__in=['admin'] + [f'student{i}' for i in range(1, 11)] + [f'parent{i}' for i in range(1, 6)] + [f'lecturer{i}' for i in range(1, 6)]).delete()
        
        self.stdout.write('Demo data deleted successfully.')
    
    def seed_users(self):
        """Seed users including admin, students, parents, and lecturers."""
        self.stdout.write('Seeding users...')
        
        # Create or get admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@school.edu',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            self.stdout.write(f'  Created admin: {admin.username}')
        else:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  Reused admin: {admin.username}')
        
        # Create students with different performance levels
        student_names = [
            ('John', 'Doe', 'STU/2024/001'),
            ('Jane', 'Smith', 'STU/2024/002'),
            ('Michael', 'Johnson', 'STU/2024/003'),
            ('Emily', 'Williams', 'STU/2024/004'),
            ('David', 'Brown', 'STU/2024/005'),
            ('Sarah', 'Jones', 'STU/2024/006'),
            ('James', 'Garcia', 'STU/2024/007'),
            ('Jennifer', 'Miller', 'STU/2024/008'),
            ('Robert', 'Davis', 'STU/2024/009'),
            ('Lisa', 'Wilson', 'STU/2024/010'),
        ]
        
        self.students = []
        for i, (first_name, last_name, student_id) in enumerate(student_names, 1):
            user, created = User.objects.get_or_create(
                username=f'student{i}',
                defaults={
                    'email': f'student{i}@school.edu',
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'student'
                }
            )
            if created:
                user.set_password('student123')
                user.save()
            else:
                user.set_password('student123')
                user.save()
            
            student, created = StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'student_id': student_id,
                    'date_of_birth': date(2000 + i, 1, 1),
                    'grade_level': 100
                }
            )
            self.students.append(student)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} student: {user.username} ({student_id})')
        
        # Create parents
        parent_names = [
            ('Richard', 'Doe', 'parent1@school.edu'),
            ('Mary', 'Smith', 'parent2@school.edu'),
            ('William', 'Johnson', 'parent3@school.edu'),
            ('Patricia', 'Williams', 'parent4@school.edu'),
            ('Thomas', 'Brown', 'parent5@school.edu'),
        ]
        
        self.parents = []
        for i, (first_name, last_name, email) in enumerate(parent_names, 1):
            user, created = User.objects.get_or_create(
                username=f'parent{i}',
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'parent'
                }
            )
            if created:
                user.set_password('parent123')
                user.save()
            else:
                user.set_password('parent123')
                user.save()
            
            parent, created = ParentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'occupation': 'Business Owner',
                    'phone_number': f'+123456780{i:02d}'
                }
            )
            self.parents.append(parent)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} parent: {user.username}')
        
        # Link parents to students (each parent linked to 2 students)
        for i, parent in enumerate(self.parents):
            # Link to 2 students
            student1 = self.students[i]
            student2 = self.students[i + 5] if i + 5 < len(self.students) else self.students[0]
            
            relation1, created = ParentStudentRelation.objects.get_or_create(
                parent=parent,
                student=student1,
                defaults={'relationship_type': 'Father' if i % 2 == 0 else 'Mother'}
            )
            
            relation2, created = ParentStudentRelation.objects.get_or_create(
                parent=parent,
                student=student2,
                defaults={'relationship_type': 'Father' if i % 2 == 0 else 'Mother'}
            )
            
            self.stdout.write(f'  Linked {parent.user.username} to {student1.student_id} and {student2.student_id}')
        
        # Create lecturers
        lecturer_names = [
            ('Dr.', 'Robert', 'Chen', 'lecturer1@school.edu'),
            ('Prof.', 'Sarah', 'Williams', 'lecturer2@school.edu'),
            ('Dr.', 'Michael', 'Brown', 'lecturer3@school.edu'),
            ('Prof.', 'Emily', 'Davis', 'lecturer4@school.edu'),
            ('Dr.', 'James', 'Wilson', 'lecturer5@school.edu'),
        ]
        
        self.lecturers = []
        for i, (title, first_name, last_name, email) in enumerate(lecturer_names, 1):
            user, created = User.objects.get_or_create(
                username=f'lecturer{i}',
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'lecturer'
                }
            )
            if created:
                user.set_password('lecturer123')
                user.save()
            else:
                user.set_password('lecturer123')
                user.save()
            
            lecturer, created = LecturerProfile.objects.update_or_create(
                user=user,
                defaults={
                    'staff_id': f'STAFF/2024/{i:03d}',
                    'rank': 'lecturer_i',
                    'date_of_birth': date(1980 + i, 1, 1)
                }
            )
            self.lecturers.append(lecturer)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} lecturer: {user.username} ({lecturer.staff_id})')
    
    def seed_academic_structure(self):
        """Seed academic sessions, semesters, levels, and courses."""
        self.stdout.write('Seeding academic structure...')
        
        # Create levels
        levels = ['100 Level', '200 Level', '300 Level', '400 Level', '500 Level']
        self.levels = []
        for level_name in levels:
            level, created = Level.objects.get_or_create(
                name=level_name
            )
            self.levels.append(level)
            action = 'Created' if created else 'Reused'
            self.stdout.write(f'  {action} level: {level_name}')
        
        # Create sessions (current and previous)
        self.sessions = []
        session_data = [
            ('2023/2024', date(2023, 9, 1), date(2024, 7, 31), False),
            ('2024/2025', date(2024, 9, 1), date(2025, 7, 31), True),
        ]
        
        for name, start_date, end_date, is_active in session_data:
            session, created = AcademicSession.objects.get_or_create(
                name=name,
                defaults={
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_active': is_active
                }
            )
            self.sessions.append(session)
            action = 'Created' if created else 'Reused'
            self.stdout.write(f'  {action} session: {name}')
        
        # Create semesters for each session
        self.semesters = []
        for session in self.sessions:
            for semester_name in ['first', 'second']:
                semester, created = Semester.objects.get_or_create(
                    name=semester_name,
                    session=session
                )
                self.semesters.append(semester)
                action = 'Created' if created else 'Reused'
                self.stdout.write(f'  {action} semester: {session.name} - {semester_name}')
        
        # Create courses (15 courses across different semesters)
        course_data = [
            ('CSC101', 'Introduction to Computer Science', 3, 0, 'first'),
            ('MTH101', 'Mathematics I', 4, 0, 'first'),
            ('PHY101', 'Physics I', 3, 0, 'first'),
            ('CHM101', 'Chemistry I', 3, 0, 'first'),
            ('ENG101', 'English Language', 2, 0, 'first'),
            ('CSC102', 'Programming Fundamentals', 3, 0, 'second'),
            ('MTH102', 'Mathematics II', 4, 0, 'second'),
            ('PHY102', 'Physics II', 3, 0, 'second'),
            ('CHM102', 'Chemistry II', 3, 0, 'second'),
            ('GST101', 'General Studies', 2, 0, 'first'),
            ('CSC201', 'Data Structures', 3, 1, 'first'),
            ('MTH201', 'Calculus I', 4, 1, 'first'),
            ('CSC202', 'Algorithms', 3, 1, 'second'),
            ('MTH202', 'Linear Algebra', 3, 1, 'second'),
            ('CSC301', 'Database Systems', 3, 2, 'first'),
        ]
        
        self.courses = []
        for course_code, course_title, credit_unit, level_index, semester_name in course_data:
            if level_index < len(self.levels):
                # Find the appropriate semester
                semester = next(s for s in self.semesters if s.name == semester_name and s.session == self.sessions[0])
                
                course, created = Course.objects.get_or_create(
                    course_code=course_code,
                    defaults={
                        'course_title': course_title,
                        'credit_unit': credit_unit,
                        'level': self.levels[level_index],
                        'semester': semester,
                        'is_active': True
                    }
                )
                self.courses.append(course)
                action = 'Created' if created else 'Reused'
                self.stdout.write(f'  {action} course: {course_code} - {course_title}')
    
    def seed_enrollments_and_grades(self):
        """Seed student enrollments, course registrations, and grades."""
        self.stdout.write('Seeding enrollments and grades...')
        
        # Enroll all students in the current session
        current_session = self.sessions[1]
        level_100 = self.levels[0]
        
        for student in self.students:
            # Create or get enrollment
            enrollment, created = StudentEnrollment.objects.get_or_create(
                student=student,
                session=current_session,
                level=level_100
            )
            action = 'Enrolled' if created else 'Reused enrollment for'
            self.stdout.write(f'  {action} {student.student_id} in {current_session.name}')
            
            # Register for courses (5-7 courses per student)
            first_semester_courses = [c for c in self.courses if c.semester.name == 'first' and c.semester.session == current_session]
            second_semester_courses = [c for c in self.courses if c.semester.name == 'second' and c.semester.session == current_session]
            
            # Register for first semester courses
            for course in random.sample(first_semester_courses, min(5, len(first_semester_courses))):
                registration, created = CourseRegistration.objects.get_or_create(
                    student=student,
                    course=course,
                    session=current_session,
                    semester=course.semester,
                    defaults={'is_carryover': False}
                )
                
                # Generate realistic grade based on student performance tier
                student_index = self.students.index(student)
                score = self.generate_realistic_score(student_index)
                
                grade, created = Grade.objects.get_or_create(
                    registration=registration,
                    defaults={'score': score}
                )
                if not created:
                    # Update existing grade with new score
                    grade.score = score
                    grade.save()
            
            # Register for second semester courses
            for course in random.sample(second_semester_courses, min(4, len(second_semester_courses))):
                registration, created = CourseRegistration.objects.get_or_create(
                    student=student,
                    course=course,
                    session=current_session,
                    semester=course.semester,
                    defaults={'is_carryover': False}
                )
                
                student_index = self.students.index(student)
                score = self.generate_realistic_score(student_index)
                
                grade, created = Grade.objects.get_or_create(
                    registration=registration,
                    defaults={'score': score}
                )
                if not created:
                    # Update existing grade with new score
                    grade.score = score
                    grade.save()
            
            self.stdout.write(f'  Created registrations and grades for {student.student_id}')
    
    def generate_realistic_score(self, student_index):
        """
        Generate realistic score based on student performance tier.
        
        Args:
            student_index: Index of the student in the students list
            
        Returns:
            Realistic score between 0 and 100
        """
        # Create different performance tiers
        if student_index < 2:  # High performers (4.0+ CGPA)
            return random.randint(70, 95)
        elif student_index < 5:  # Good performers (3.0-3.9 CGPA)
            return random.randint(60, 85)
        elif student_index < 8:  # Average performers (2.0-2.9 CGPA)
            return random.randint(45, 75)
        else:  # Students on probation (<2.0 CGPA)
            return random.randint(30, 65)
    
    def seed_attendance(self):
        """Seed attendance records for students."""
        self.stdout.write('Seeding attendance records...')
        
        current_session = self.sessions[1]
        
        for student in self.students:
            # Get student's registrations
            registrations = CourseRegistration.objects.filter(
                student=student,
                session=current_session
            )
            
            for registration in registrations:
                # Create attendance records for 10-15 class days
                num_classes = random.randint(10, 15)
                base_date = date(2024, 9, 1)  # Use a fixed base date since semester doesn't have start_date
                
                for i in range(num_classes):
                    class_date = base_date + timedelta(days=i * 7)  # Weekly classes
                    
                    # Generate realistic attendance (80-95% present)
                    status = 'present' if random.random() < 0.85 else 'absent'
                    
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        course=registration.course,
                        date=class_date,
                        defaults={'status': status}
                    )
                    if not created:
                        # Update existing attendance with new status
                        attendance.status = status
                        attendance.save()
            
            self.stdout.write(f'  Created attendance records for {student.student_id}')
