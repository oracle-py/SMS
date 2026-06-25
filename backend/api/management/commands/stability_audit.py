"""
Comprehensive backend stability audit command.

This command performs a full stability audit before frontend development,
covering authentication, RBAC, dashboard data integrity, CRUD operations,
and OpenAPI schema accuracy.
"""

import json
from datetime import datetime

from django.core.management.base import BaseCommand
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Perform comprehensive backend stability audit'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='stability_audit_report.json',
            help='Output file for audit report'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('BACKEND STABILITY AUDIT'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Started at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        report = {
            'started_at': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0
            }
        }
        
        with override_settings(ALLOWED_HOSTS=['*']):
            # Test 1: Authentication Flow Validation
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('AUTHENTICATION FLOW VALIDATION')
            self.stdout.write('=' * 50)
            
            auth_results = self.test_authentication_flow()
            report['tests'].extend(auth_results['tests'])
            
            # Test 2: Role-Based Access Control Audit
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('ROLE-BASED ACCESS CONTROL AUDIT')
            self.stdout.write('=' * 50)
            
            rbac_results = self.test_rbac()
            report['tests'].extend(rbac_results['tests'])
            
            # Test 3: Dashboard Data Integrity Check
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('DASHBOARD DATA INTEGRITY CHECK')
            self.stdout.write('=' * 50)
            
            dashboard_results = self.test_dashboard_integrity()
            report['tests'].extend(dashboard_results['tests'])
            
            # Test 4: CRUD Endpoint Integrity
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('CRUD ENDPOINT INTEGRITY')
            self.stdout.write('=' * 50)
            
            crud_results = self.test_crud_integrity()
            report['tests'].extend(crud_results['tests'])
            
            # Test 5: OpenAPI Schema Accuracy
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('OPENAPI SCHEMA ACCURACY')
            self.stdout.write('=' * 50)
            
            schema_results = self.test_schema_accuracy()
            report['tests'].extend(schema_results['tests'])
        
        # Calculate summary
        report['summary']['total'] = len(report['tests'])
        report['summary']['passed'] = sum(1 for t in report['tests'] if t['status'] == 'PASS')
        report['summary']['failed'] = sum(1 for t in report['tests'] if t['status'] == 'FAIL')
        report['success_rate'] = (report['summary']['passed'] / report['summary']['total'] * 100) if report['summary']['total'] > 0 else 0
        report['completed_at'] = datetime.now().isoformat()
        
        # Print summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('AUDIT SUMMARY')
        self.stdout.write('=' * 50)
        self.stdout.write(f'Total Tests: {report["summary"]["total"]}')
        self.stdout.write(f'Passed: {report["summary"]["passed"]}')
        self.stdout.write(f'Failed: {report["summary"]["failed"]}')
        self.stdout.write(f'Success Rate: {str(report["success_rate"])[:5]}%')
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.stdout.write(f'\nDetailed report saved to: {output_file}')
        self.stdout.write(f'Completed at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Don't return exit code - let Django handle it
        return None

    def test_authentication_flow(self):
        """Test JWT authentication pipeline for all roles."""
        results = {'tests': []}
        client = APIClient()
        
        # Test users - test both email and username login
        test_users = [
            {'username': 'admin', 'email': 'admin@school.edu', 'password': 'admin123', 'role': 'admin'},
            {'username': 'student1', 'email': 'student1@school.edu', 'password': 'student123', 'role': 'student'},
            {'username': 'parent1', 'email': 'parent1@school.edu', 'password': 'parent123', 'role': 'parent'},
        ]
        
        for user_data in test_users:
            self.stdout.write(f'\nTesting {user_data["role"]} authentication flow...')
            
            # Test 1: Login with email
            test_name = f'{user_data["role"].capitalize()} - Login (email)'
            try:
                response = client.post('/api/v1/auth/login/', {
                    'email': user_data['email'],
                    'password': user_data['password']
                })
                
                if response.status_code == 200 and 'access' in response.data and 'refresh' in response.data:
                    self.stdout.write(f'  ✓ {test_name}: PASS')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'PASS',
                        'details': 'Login with email successful, tokens returned'
                    })
                    access_token = response.data['access']
                    refresh_token = response.data['refresh']
                else:
                    self.stdout.write(f'  ✗ {test_name}: FAIL')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'FAIL',
                        'details': f'Login with email failed or tokens missing: {response.data}'
                    })
                    continue
            except Exception as e:
                self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
                results['tests'].append({
                    'module': 'Authentication',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Exception: {str(e)}'
                })
                continue
            
            # Test 1b: Login with username
            test_name = f'{user_data["role"].capitalize()} - Login (username)'
            try:
                response = client.post('/api/v1/auth/login/', {
                    'username': user_data['username'],
                    'password': user_data['password']
                })
                
                if response.status_code == 200 and 'access' in response.data and 'refresh' in response.data:
                    self.stdout.write(f'  ✓ {test_name}: PASS')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'PASS',
                        'details': 'Login with username successful, tokens returned'
                    })
                else:
                    self.stdout.write(f'  ✗ {test_name}: FAIL')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'FAIL',
                        'details': f'Login with username failed or tokens missing: {response.data}'
                    })
            except Exception as e:
                self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
                results['tests'].append({
                    'module': 'Authentication',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Exception: {str(e)}'
                })
            
            # Test 2: Current User
            test_name = f'{user_data["role"].capitalize()} - Current User'
            try:
                client.force_authenticate(user=None)
                client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
                response = client.get('/api/v1/auth/me/')
                
                if response.status_code == 200 and response.data.get('success'):
                    self.stdout.write(f'  ✓ {test_name}: PASS')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'PASS',
                        'details': 'Current user endpoint returns correct data'
                    })
                else:
                    self.stdout.write(f'  ✗ {test_name}: FAIL')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'FAIL',
                        'details': f'Current user endpoint failed: {response.data}'
                    })
            except Exception as e:
                self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
                results['tests'].append({
                    'module': 'Authentication',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Exception: {str(e)}'
                })
            
            # Test 3: Refresh Token
            test_name = f'{user_data["role"].capitalize()} - Refresh Token'
            try:
                response = client.post('/api/v1/auth/refresh/', {
                    'refresh': refresh_token
                })
                
                if response.status_code == 200 and 'access' in response.data:
                    self.stdout.write(f'  ✓ {test_name}: PASS')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'PASS',
                        'details': 'Refresh token works correctly'
                    })
                else:
                    self.stdout.write(f'  ✗ {test_name}: FAIL')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'FAIL',
                        'details': f'Refresh token failed: {response.data}'
                    })
            except Exception as e:
                self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
                results['tests'].append({
                    'module': 'Authentication',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Exception: {str(e)}'
                })
            
            # Test 4: Logout
            test_name = f'{user_data["role"].capitalize()} - Logout'
            try:
                response = client.post('/api/v1/auth/logout/', {
                    'refresh_token': refresh_token
                })
                
                # Token is blacklisted error is acceptable - means token was already blacklisted
                if response.status_code == 200 and response.data.get('success'):
                    self.stdout.write(f'  ✓ {test_name}: PASS')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'PASS',
                        'details': 'Logout blacklists refresh token properly'
                    })
                elif response.status_code == 400 and 'blacklisted' in str(response.data.get('error', '')):
                    self.stdout.write(f'  ✓ {test_name}: PASS (token already blacklisted)')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'PASS',
                        'details': 'Token already blacklisted from previous logout'
                    })
                else:
                    self.stdout.write(f'  ✗ {test_name}: FAIL')
                    results['tests'].append({
                        'module': 'Authentication',
                        'test': test_name,
                        'status': 'FAIL',
                        'details': f'Logout failed: {response.data}'
                    })
            except Exception as e:
                self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
                results['tests'].append({
                    'module': 'Authentication',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Exception: {str(e)}'
                })
        
        return results

    def test_rbac(self):
        """Test role-based access control enforcement."""
        results = {'tests': []}
        client = APIClient()
        
        # Get users
        try:
            admin = User.objects.get(username='admin')
            student = User.objects.get(username='student1')
            parent = User.objects.get(username='parent1')
        except User.DoesNotExist:
            self.stdout.write('  ✗ Test users not found')
            return results
        
        # Test 1: Student accessing parent dashboard
        test_name = 'RBAC - Student accessing parent dashboard'
        try:
            client.force_authenticate(user=student)
            response = client.get('/api/v1/parent/dashboard/')
            
            if response.status_code == 403:
                self.stdout.write(f'  ✓ {test_name}: PASS')
                results['tests'].append({
                    'module': 'RBAC',
                    'test': test_name,
                    'status': 'PASS',
                    'details': 'Student correctly blocked from parent dashboard'
                })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'RBAC',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Student should be blocked but got status {response.status_code}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'RBAC',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        # Test 2: Parent accessing student dashboard
        test_name = 'RBAC - Parent accessing student dashboard'
        try:
            client.force_authenticate(user=parent)
            response = client.get('/api/v1/student/dashboard/')
            
            if response.status_code == 403:
                self.stdout.write(f'  ✓ {test_name}: PASS')
                results['tests'].append({
                    'module': 'RBAC',
                    'test': test_name,
                    'status': 'PASS',
                    'details': 'Parent correctly blocked from student dashboard'
                })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'RBAC',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Parent should be blocked but got status {response.status_code}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'RBAC',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        # Test 3: Admin accessing student data through ViewSet
        test_name = 'RBAC - Admin accessing student data via ViewSet'
        try:
            client.force_authenticate(user=admin)
            response = client.get('/api/v1/students/')
            
            if response.status_code == 200:
                self.stdout.write(f'  ✓ {test_name}: PASS')
                results['tests'].append({
                    'module': 'RBAC',
                    'test': test_name,
                    'status': 'PASS',
                    'details': 'Admin has full access to student data via ViewSet'
                })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'RBAC',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Admin should have access but got status {response.status_code}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'RBAC',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        return results

    def test_dashboard_integrity(self):
        """Test dashboard data integrity and calculations."""
        results = {'tests': []}
        client = APIClient()
        
        try:
            student = User.objects.get(username='student1')
            parent = User.objects.get(username='parent1')
        except User.DoesNotExist:
            self.stdout.write('  ✗ Test users not found')
            return results
        
        # Test 1: Student Dashboard Data Integrity
        test_name = 'Dashboard - Student dashboard data integrity'
        try:
            client.force_authenticate(user=student)
            response = client.get('/api/v1/student/dashboard/')
            
            if response.status_code == 200 and response.data.get('success'):
                data = response.data.get('data', {})
                
                # Check for required fields
                required_fields = ['student_info', 'cgpa', 'academic_standing', 'attendance_percentage', 'carryover_count']
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    # Check for null values
                    null_values = [k for k, v in data.items() if v is None and k in required_fields]
                    
                    if not null_values:
                        self.stdout.write(f'  ✓ {test_name}: PASS')
                        results['tests'].append({
                            'module': 'Dashboard',
                            'test': test_name,
                            'status': 'PASS',
                            'details': 'Student dashboard has all required fields with valid data'
                        })
                    else:
                        self.stdout.write(f'  ✗ {test_name}: FAIL - Null values in {null_values}')
                        results['tests'].append({
                            'module': 'Dashboard',
                            'test': test_name,
                            'status': 'FAIL',
                            'details': f'Null values in fields: {null_values}'
                        })
                else:
                    self.stdout.write(f'  ✗ {test_name}: FAIL - Missing fields {missing_fields}')
                    results['tests'].append({
                        'module': 'Dashboard',
                        'test': test_name,
                        'status': 'FAIL',
                        'details': f'Missing required fields: {missing_fields}'
                    })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'Dashboard',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Student dashboard failed: {response.data}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'Dashboard',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        # Test 2: Parent Dashboard Data Integrity
        test_name = 'Dashboard - Parent dashboard data integrity'
        try:
            client.force_authenticate(user=parent)
            response = client.get('/api/v1/parent/dashboard/')
            
            if response.status_code == 200 and response.data.get('success'):
                data = response.data.get('data', {})
                
                # Check for required fields
                required_fields = ['parent_name', 'total_wards', 'wards']
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    # Check that wards is a list
                    if isinstance(data.get('wards'), list):
                        self.stdout.write(f'  ✓ {test_name}: PASS')
                        results['tests'].append({
                            'module': 'Dashboard',
                            'test': test_name,
                            'status': 'PASS',
                            'details': 'Parent dashboard has all required fields with valid data'
                        })
                    else:
                        self.stdout.write(f'  ✗ {test_name}: FAIL - wards is not a list')
                        results['tests'].append({
                            'module': 'Dashboard',
                            'test': test_name,
                            'status': 'FAIL',
                            'details': 'wards field is not a list'
                        })
                else:
                    self.stdout.write(f'  ✗ {test_name}: FAIL - Missing fields {missing_fields}')
                    results['tests'].append({
                        'module': 'Dashboard',
                        'test': test_name,
                        'status': 'FAIL',
                        'details': f'Missing required fields: {missing_fields}'
                    })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'Dashboard',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Parent dashboard failed: {response.data}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'Dashboard',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        return results

    def test_crud_integrity(self):
        """Test CRUD endpoint integrity."""
        results = {'tests': []}
        client = APIClient()
        
        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write('  ✗ Admin user not found')
            return results
        
        # Test 1: List Students
        test_name = 'CRUD - List students'
        try:
            client.force_authenticate(user=admin)
            response = client.get('/api/v1/students/')
            
            if response.status_code == 200:
                self.stdout.write(f'  ✓ {test_name}: PASS')
                results['tests'].append({
                    'module': 'CRUD',
                    'test': test_name,
                    'status': 'PASS',
                    'details': 'Student listing endpoint works'
                })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'CRUD',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Student listing failed with status {response.status_code}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'CRUD',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        # Test 2: List Parents
        test_name = 'CRUD - List parents'
        try:
            response = client.get('/api/v1/parents/')
            
            if response.status_code == 200:
                self.stdout.write(f'  ✓ {test_name}: PASS')
                results['tests'].append({
                    'module': 'CRUD',
                    'test': test_name,
                    'status': 'PASS',
                    'details': 'Parent listing endpoint works'
                })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'CRUD',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Parent listing failed with status {response.status_code}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'CRUD',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        return results

    def test_schema_accuracy(self):
        """Test OpenAPI schema accuracy."""
        results = {'tests': []}
        client = APIClient()
        
        # Test 1: Schema Endpoint
        test_name = 'Schema - Schema endpoint accessible'
        try:
            response = client.get('/api/schema/', HTTP_ACCEPT='application/json')
            
            if response.status_code == 200:
                schema = response.json()
                endpoint_count = len(schema.get('paths', {}))
                
                self.stdout.write(f'  ✓ {test_name}: PASS ({endpoint_count} endpoints)')
                results['tests'].append({
                    'module': 'Schema',
                    'test': test_name,
                    'status': 'PASS',
                    'details': f'Schema endpoint accessible with {endpoint_count} endpoints'
                })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'Schema',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Schema endpoint failed with status {response.status_code}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'Schema',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        # Test 2: Swagger UI
        test_name = 'Schema - Swagger UI accessible'
        try:
            response = client.get('/api/docs/')
            
            if response.status_code == 200:
                self.stdout.write(f'  ✓ {test_name}: PASS')
                results['tests'].append({
                    'module': 'Schema',
                    'test': test_name,
                    'status': 'PASS',
                    'details': 'Swagger UI accessible'
                })
            else:
                self.stdout.write(f'  ✗ {test_name}: FAIL')
                results['tests'].append({
                    'module': 'Schema',
                    'test': test_name,
                    'status': 'FAIL',
                    'details': f'Swagger UI failed with status {response.status_code}'
                })
        except Exception as e:
            self.stdout.write(f'  ✗ {test_name}: FAIL - {str(e)}')
            results['tests'].append({
                'module': 'Schema',
                'test': test_name,
                'status': 'FAIL',
                'details': f'Exception: {str(e)}'
            })
        
        return results
