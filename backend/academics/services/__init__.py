"""
Academic services for student monitoring system.

This module provides business logic for academic calculations including
GPA, CGPA, carryover detection, academic standing, and semester summaries.
"""

from .academic_services import (
    GPAService,
    AcademicStandingService,
    SemesterSummaryService,
    StudentDashboardService,
)

__all__ = [
    'GPAService',
    'AcademicStandingService',
    'SemesterSummaryService',
    'StudentDashboardService',
]
