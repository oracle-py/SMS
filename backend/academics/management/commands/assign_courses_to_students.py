"""
Management command to assign existing courses to existing students.

This command retroactively assigns courses to students based on their grade level.
It's useful for initial data setup or when courses are added after students are registered.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
import logging

from academics.models import Course, CourseRegistration, AcademicSession, Level
from users.models import StudentProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Assign existing courses to existing students based on grade level'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually assigning courses',
        )
        parser.add_argument(
            '--grade-level',
            type=int,
            help='Only assign courses for a specific grade level (e.g., 100, 200)',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        specific_grade_level = options.get('grade_level')

        self.stdout.write(self.style.SUCCESS('Starting course assignment...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        try:
            # Get current academic session
            current_session = AcademicSession.objects.filter(is_current=True).first()
            if not current_session:
                self.stdout.write(self.style.WARNING('No current academic session found, using first available'))
                current_session = AcademicSession.objects.first()
            
            if not current_session:
                self.stdout.write(self.style.ERROR('No academic session available'))
                return
            
            self.stdout.write(f'Using session: {current_session.name}')

            # Get all levels
            levels = Level.objects.all()
            self.stdout.write(f'Found {levels.count()} levels in database')

            total_assigned = 0
            total_skipped = 0

            for level in levels:
                # Parse grade level from level name
                level_name = level.name
                try:
                    grade_level = int(level_name.split()[0])
                except (ValueError, IndexError):
                    self.stdout.write(self.style.WARNING(f'Skipping level {level_name} - cannot parse grade level'))
                    continue

                # Skip if specific grade level is requested and doesn't match
                if specific_grade_level and grade_level != specific_grade_level:
                    continue

                self.stdout.write(f'\nProcessing level {level_name} (grade {grade_level})...')

                # Get students in this grade level
                students = StudentProfile.objects.filter(grade_level=grade_level)
                self.stdout.write(f'  Found {students.count()} students')

                if students.count() == 0:
                    self.stdout.write(f'  No students in this level, skipping')
                    continue

                # Get courses for this level
                courses = Course.objects.filter(level=level, is_active=True)
                if courses.count() == 0:
                    self.stdout.write(self.style.WARNING(f'  No active courses for this level, trying all courses'))
                    courses = Course.objects.filter(level=level)
                
                self.stdout.write(f'  Found {courses.count()} courses')

                if courses.count() == 0:
                    self.stdout.write(self.style.WARNING(f'  No courses for this level, skipping'))
                    continue

                # Assign courses to students
                level_assigned = 0
                level_skipped = 0

                for student in students:
                    for course in courses:
                        # Check if already registered
                        existing = CourseRegistration.objects.filter(
                            student=student,
                            course=course,
                            session=current_session,
                            semester=course.semester
                        ).exists()

                        if not existing:
                            if not dry_run:
                                CourseRegistration.objects.create(
                                    student=student,
                                    course=course,
                                    session=current_session,
                                    semester=course.semester,
                                    is_carryover=False
                                )
                            level_assigned += 1
                            self.stdout.write(f'    Assigned {course.course_code} to {student.student_id}')
                        else:
                            level_skipped += 1

                total_assigned += level_assigned
                total_skipped += level_skipped
                self.stdout.write(f'  Level {grade_level}: {level_assigned} assigned, {level_skipped} skipped')

            self.stdout.write(self.style.SUCCESS(f'\nTotal: {total_assigned} courses assigned, {total_skipped} already registered'))

            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes were made'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            logger.error(f'Error in assign_courses_to_students command: {e}', exc_info=True)
