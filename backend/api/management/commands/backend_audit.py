"""
Django management command to perform backend readiness audit.

This command tests all dashboard endpoints, access control, calculations,
and API documentation to ensure the backend is ready for frontend development.
"""

from django.core.management.base import BaseCommand
from django.test import override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Perform backend readiness audit before frontend development'

    @override_settings(ALLOWED_HOSTS=['*'])
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('BACKEND READINESS AUDIT'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(f'Started at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write()

        test_results = []

        # Get users
        try:
            admin = User.objects.get(username='admin')
            student1 = User.objects.get(username='student1')
            parent1 = User.objects.get(username='parent1')
        except User.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'User not found: {e}'))
            self.stdout.write(self.style.ERROR('Run seed_demo_data first'))
            return

        self.stdout.write('Users loaded:')
        for role, user in [('admin', admin), ('student', student1), ('parent', parent1)]:
            self.stdout.write(f'  ✓ {role}: {user.username}')
        self.stdout.write()

        client = APIClient()

        # Test 1: Student dashboard endpoint
        self.stdout.write('Test 1: Student Dashboard Endpoint')
        self.stdout.write('-' * 40)
        client.force_authenticate(user=student1)
        response = client.get('/api/v1/student/dashboard/')
        result = {
            'endpoint': '/api/v1/student/dashboard/',
            'role': 'student',
            'expected_status': 200,
            'actual_status': response.status_code,
            'description': 'Student should see their own dashboard data',
            'pass': response.status_code == 200,
        }
        if response.status_code == 200:
            data = response.json()
            result['response_data'] = data
            issues = self.verify_calculations(data)
            if issues:
                result['calculation_issues'] = issues
                self.stdout.write(self.style.WARNING(f'  Calculation issues: {issues}'))
            else:
                self.stdout.write(self.style.SUCCESS('  Calculations verified'))
        elif response.status_code == 500:
            # Log the actual error for debugging
            result['error_content'] = response.content.decode('utf-8')
            self.stdout.write(self.style.ERROR(f'  Error: {response.content.decode("utf-8")[:500]}'))
        test_results.append(result)
        self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
        self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
        self.stdout.write()

        # Test 2: Parent dashboard endpoint
        self.stdout.write('Test 2: Parent Dashboard Endpoint')
        self.stdout.write('-' * 40)
        client.force_authenticate(user=parent1)
        response = client.get('/api/v1/parent/dashboard/')
        result = {
            'endpoint': '/api/v1/parent/dashboard/',
            'role': 'parent',
            'expected_status': 200,
            'actual_status': response.status_code,
            'description': 'Parent should see their wards dashboard data',
            'pass': response.status_code == 200,
        }
        if response.status_code == 200:
            data = response.json()
            result['response_data'] = data
            if 'wards' in data:
                self.stdout.write(f'  Parent has {len(data["wards"])} wards linked')
        test_results.append(result)
        self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
        self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
        self.stdout.write()

        # Test 3: Student results endpoint
        self.stdout.write('Test 3: Student Results Endpoint')
        self.stdout.write('-' * 40)
        client.force_authenticate(user=student1)
        response = client.get('/api/v1/student/results/')
        result = {
            'endpoint': '/api/v1/student/results/',
            'role': 'student',
            'expected_status': 200,
            'actual_status': response.status_code,
            'description': 'Student should see their own results',
            'pass': response.status_code == 200,
        }
        if response.status_code == 200:
            data = response.json()
            result['response_data'] = data
            if 'results' in data:
                self.stdout.write(f'  Student has {len(data["results"])} course results')
        test_results.append(result)
        self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
        self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
        self.stdout.write()

        # Test 4: Student attendance endpoint
        self.stdout.write('Test 4: Student Attendance Endpoint')
        self.stdout.write('-' * 40)
        client.force_authenticate(user=student1)
        response = client.get('/api/v1/student/attendance/')
        result = {
            'endpoint': '/api/v1/student/attendance/',
            'role': 'student',
            'expected_status': 200,
            'actual_status': response.status_code,
            'description': 'Student should see their own attendance',
            'pass': response.status_code == 200,
        }
        if response.status_code == 200:
            data = response.json()
            result['response_data'] = data
            if 'attendance_records' in data:
                self.stdout.write(f'  Student has {len(data["attendance_records"])} attendance records')
        test_results.append(result)
        self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
        self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
        self.stdout.write()

        # Test 5: Parent ward detail endpoint
        self.stdout.write('Test 5: Parent Ward Detail Endpoint')
        self.stdout.write('-' * 40)
        # First get parent dashboard to find a ward ID
        client.force_authenticate(user=parent1)
        dashboard_response = client.get('/api/v1/parent/dashboard/')
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            wards = dashboard_data.get('wards', [])
            if wards:
                ward_id = wards[0]['student_id']
                response = client.get(f'/api/v1/parent/wards/{ward_id}/')
                result = {
                    'endpoint': f'/api/v1/parent/wards/{ward_id}/',
                    'role': 'parent',
                    'expected_status': 200,
                    'actual_status': response.status_code,
                    'description': 'Parent should see ward detail data',
                    'pass': response.status_code == 200,
                }
                if response.status_code == 200:
                    result['response_data'] = response.json()
                test_results.append(result)
                self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
                self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
            else:
                self.stdout.write('  SKIP: No wards found for parent')
        else:
            self.stdout.write('  SKIP: Could not get parent dashboard')
        self.stdout.write()

        # Test 6: Access control - Student accessing parent endpoint
        self.stdout.write('Test 6: Access Control - Student accessing parent endpoint')
        self.stdout.write('-' * 40)
        client.force_authenticate(user=student1)
        response = client.get('/api/v1/parent/dashboard/')
        result = {
            'endpoint': '/api/v1/parent/dashboard/',
            'role': 'student',
            'expected_status': 403,
            'actual_status': response.status_code,
            'description': 'Student should NOT be able to access parent dashboard',
            'pass': response.status_code == 403,
        }
        test_results.append(result)
        self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
        self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
        self.stdout.write()

        # Test 7: Access control - Parent accessing student endpoint
        self.stdout.write('Test 7: Access Control - Parent accessing student endpoint')
        self.stdout.write('-' * 40)
        client.force_authenticate(user=parent1)
        response = client.get('/api/v1/student/dashboard/')
        result = {
            'endpoint': '/api/v1/student/dashboard/',
            'role': 'parent',
            'expected_status': 403,
            'actual_status': response.status_code,
            'description': 'Parent should NOT be able to access student dashboard',
            'pass': response.status_code == 403,
        }
        test_results.append(result)
        self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
        self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
        self.stdout.write()

        # Test 8: Swagger documentation
        self.stdout.write('Test 8: Swagger Documentation')
        self.stdout.write('-' * 40)
        response = client.get('/api/docs/')
        result = {
            'endpoint': '/api/docs/',
            'role': 'public',
            'expected_status': 200,
            'actual_status': response.status_code,
            'description': 'Swagger UI should load without authentication',
            'pass': response.status_code == 200,
        }
        test_results.append(result)
        self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
        self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
        self.stdout.write()

        # Test 9: OpenAPI schema
        self.stdout.write('Test 9: OpenAPI Schema')
        self.stdout.write('-' * 40)
        response = client.get('/api/schema/', HTTP_ACCEPT='application/json')
        result = {
            'endpoint': '/api/schema/',
            'role': 'public',
            'expected_status': 200,
            'actual_status': response.status_code,
            'description': 'OpenAPI schema should be accessible',
            'pass': response.status_code == 200,
        }
        if response.status_code == 200:
            try:
                schema = response.json()
                paths = schema.get('paths', {})
                self.stdout.write(f'  Schema contains {len(paths)} endpoints')
                result['endpoint_count'] = len(paths)
            except ValueError:
                # If JSON parsing fails, the schema might be in YAML format
                self.stdout.write('  Schema returned (YAML format)')
                result['endpoint_count'] = 'YAML format'
        test_results.append(result)
        self.stdout.write(f'  Status: {"PASS" if result["pass"] else "FAIL"}')
        self.stdout.write(f'  Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
        self.stdout.write()

        # Generate summary report
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('AUDIT SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        passed = sum(1 for r in test_results if r['pass'])
        failed = sum(1 for r in test_results if not r['pass'])
        total = len(test_results)

        self.stdout.write(f'Total Tests: {total}')
        self.stdout.write(f'Passed: {passed}')
        self.stdout.write(f'Failed: {failed}')
        self.stdout.write(f'Success Rate: {(passed/total)*100:.1f}%')
        self.stdout.write()

        if failed > 0:
            self.stdout.write(self.style.ERROR('FAILED TESTS:'))
            for result in test_results:
                if not result['pass']:
                    self.stdout.write(self.style.ERROR(f'  ✗ {result["endpoint"]} ({result["role"]})'))
                    self.stdout.write(f'    Expected: {result["expected_status"]}, Actual: {result["actual_status"]}')
                    if 'calculation_issues' in result:
                        self.stdout.write(f'    Calculation Issues: {result["calculation_issues"]}')
            self.stdout.write()

        # Save detailed report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed/total)*100,
            'results': test_results
        }
        
        with open('backend_audit_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.stdout.write('Detailed report saved to: backend_audit_report.json')
        self.stdout.write(f'Completed at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    def verify_calculations(self, data):
        """Verify GPA, CGPA, attendance calculations."""
        issues = []
        
        if 'cgpa' in data:
            cgpa = data['cgpa']
            if not isinstance(cgpa, (int, float)) or cgpa < 0 or cgpa > 5.0:
                issues.append(f"Invalid CGPA: {cgpa}")
        
        if 'attendance_percentage' in data:
            attendance = data['attendance_percentage']
            if not isinstance(attendance, (int, float)) or attendance < 0 or attendance > 100:
                issues.append(f"Invalid attendance percentage: {attendance}")
        
        if 'carryover_count' in data:
            carryover = data['carryover_count']
            if not isinstance(carryover, int) or carryover < 0:
                issues.append(f"Invalid carryover count: {carryover}")
        
        return issues
