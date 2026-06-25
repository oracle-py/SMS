"""
Backend Readiness Audit Script

This script tests all dashboard endpoints, access control, calculations,
and API documentation to ensure the backend is ready for frontend development.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8001/api/v1'
AUTH_URL = f'{BASE_URL}/auth/login/'

# Test credentials
CREDENTIALS = {
    'admin': {'username': 'admin', 'password': 'admin123'},
    'student': {'username': 'student1', 'password': 'student123'},
    'parent': {'username': 'parent1', 'password': 'parent123'},
}

# Test results storage
test_results = []

def get_token(username, password):
    """Get JWT token for user."""
    response = requests.post(AUTH_URL, json={'username': username, 'password': password})
    if response.status_code == 200:
        return response.json().get('access')
    return None

def test_endpoint(endpoint, token, role, expected_status=200, description=''):
    """Test an endpoint with given token."""
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    try:
        response = requests.get(f'{BASE_URL}{endpoint}', headers=headers)
        result = {
            'endpoint': endpoint,
            'role': role,
            'expected_status': expected_status,
            'actual_status': response.status_code,
            'description': description,
            'pass': response.status_code == expected_status,
            'response_data': response.json() if response.status_code == 200 else None
        }
        test_results.append(result)
        return result
    except Exception as e:
        result = {
            'endpoint': endpoint,
            'role': role,
            'expected_status': expected_status,
            'actual_status': 0,
            'description': description,
            'pass': False,
            'error': str(e)
        }
        test_results.append(result)
        return result

def verify_calculations(data):
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

def main():
    """Run the backend readiness audit."""
    print("=" * 80)
    print("BACKEND READINESS AUDIT")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get tokens
    print("Getting authentication tokens...")
    tokens = {}
    for role, creds in CREDENTIALS.items():
        token = get_token(creds['username'], creds['password'])
        if token:
            tokens[role] = token
            print(f"  ✓ {role}: {creds['username']}")
        else:
            print(f"  ✗ {role}: Failed to get token")
    print()
    
    if not tokens:
        print("ERROR: Could not get any tokens. Exiting.")
        return
    
    # Test 1: Student dashboard endpoint
    print("Test 1: Student Dashboard Endpoint")
    print("-" * 40)
    if 'student' in tokens:
        result = test_endpoint(
            '/student/dashboard/',
            tokens['student'],
            'student',
            expected_status=200,
            description='Student should see their own dashboard data'
        )
        if result['pass'] and result['response_data']:
            issues = verify_calculations(result['response_data'])
            if issues:
                print(f"  Calculation issues: {issues}")
                result['calculation_issues'] = issues
        print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
    else:
        print("  SKIP: No student token available")
    print()
    
    # Test 2: Parent dashboard endpoint
    print("Test 2: Parent Dashboard Endpoint")
    print("-" * 40)
    if 'parent' in tokens:
        result = test_endpoint(
            '/parent/dashboard/',
            tokens['parent'],
            'parent',
            expected_status=200,
            description='Parent should see their wards dashboard data'
        )
        if result['pass'] and result['response_data']:
            data = result['response_data']
            if 'wards' in data and len(data['wards']) > 0:
                print(f"  Parent has {len(data['wards'])} wards linked")
        print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
    else:
        print("  SKIP: No parent token available")
    print()
    
    # Test 3: Student results endpoint
    print("Test 3: Student Results Endpoint")
    print("-" * 40)
    if 'student' in tokens:
        result = test_endpoint(
            '/student/results/',
            tokens['student'],
            'student',
            expected_status=200,
            description='Student should see their own results'
        )
        if result['pass'] and result['response_data']:
            data = result['response_data']
            if 'results' in data:
                print(f"  Student has {len(data['results'])} course results")
        print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
    else:
        print("  SKIP: No student token available")
    print()
    
    # Test 4: Student attendance endpoint
    print("Test 4: Student Attendance Endpoint")
    print("-" * 40)
    if 'student' in tokens:
        result = test_endpoint(
            '/student/attendance/',
            tokens['student'],
            'student',
            expected_status=200,
            description='Student should see their own attendance'
        )
        if result['pass'] and result['response_data']:
            data = result['response_data']
            if 'attendance_records' in data:
                print(f"  Student has {len(data['attendance_records'])} attendance records")
        print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
    else:
        print("  SKIP: No student token available")
    print()
    
    # Test 5: Parent ward detail endpoint
    print("Test 5: Parent Ward Detail Endpoint")
    print("-" * 40)
    if 'parent' in tokens:
        # First get parent dashboard to find a ward ID
        dashboard_result = test_endpoint(
            '/parent/dashboard/',
            tokens['parent'],
            'parent',
            expected_status=200,
            description='Get parent dashboard to find ward ID'
        )
        if dashboard_result['pass'] and dashboard_result['response_data']:
            wards = dashboard_result['response_data'].get('wards', [])
            if wards:
                ward_id = wards[0]['student_id']
                result = test_endpoint(
                    f'/parent/wards/{ward_id}/',
                    tokens['parent'],
                    'parent',
                    expected_status=200,
                    description='Parent should see ward detail data'
                )
                print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
                print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
            else:
                print("  SKIP: No wards found for parent")
        else:
            print("  SKIP: Could not get parent dashboard")
    else:
        print("  SKIP: No parent token available")
    print()
    
    # Test 6: Access control - Student accessing parent endpoint
    print("Test 6: Access Control - Student accessing parent endpoint")
    print("-" * 40)
    if 'student' in tokens:
        result = test_endpoint(
            '/parent/dashboard/',
            tokens['student'],
            'student',
            expected_status=403,
            description='Student should NOT be able to access parent dashboard'
        )
        print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
    else:
        print("  SKIP: No student token available")
    print()
    
    # Test 7: Access control - Parent accessing student endpoint
    print("Test 7: Access Control - Parent accessing student endpoint")
    print("-" * 40)
    if 'parent' in tokens:
        result = test_endpoint(
            '/student/dashboard/',
            tokens['parent'],
            'parent',
            expected_status=403,
            description='Parent should NOT be able to access student dashboard'
        )
        print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
    else:
        print("  SKIP: No parent token available")
    print()
    
    # Test 8: Swagger documentation
    print("Test 8: Swagger Documentation")
    print("-" * 40)
    try:
        response = requests.get(f'{BASE_URL}/../docs/')
        result = {
            'endpoint': '/api/docs/',
            'role': 'public',
            'expected_status': 200,
            'actual_status': response.status_code,
            'description': 'Swagger UI should load without authentication',
            'pass': response.status_code == 200
        }
        test_results.append(result)
        print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
    except Exception as e:
        result = {
            'endpoint': '/api/docs/',
            'role': 'public',
            'expected_status': 200,
            'actual_status': 0,
            'description': 'Swagger UI should load without authentication',
            'pass': False,
            'error': str(e)
        }
        test_results.append(result)
        print(f"  Status: FAIL - {str(e)}")
    print()
    
    # Test 9: OpenAPI schema
    print("Test 9: OpenAPI Schema")
    print("-" * 40)
    try:
        response = requests.get(f'{BASE_URL}/../schema/')
        result = {
            'endpoint': '/api/schema/',
            'role': 'public',
            'expected_status': 200,
            'actual_status': response.status_code,
            'description': 'OpenAPI schema should be accessible',
            'pass': response.status_code == 200
        }
        test_results.append(result)
        if result['pass']:
            schema = response.json()
            paths = schema.get('paths', {})
            print(f"  Schema contains {len(paths)} endpoints")
        print(f"  Status: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  Expected: {result['expected_status']}, Actual: {result['actual_status']}")
    except Exception as e:
        result = {
            'endpoint': '/api/schema/',
            'role': 'public',
            'expected_status': 200,
            'actual_status': 0,
            'description': 'OpenAPI schema should be accessible',
            'pass': False,
            'error': str(e)
        }
        test_results.append(result)
        print(f"  Status: FAIL - {str(e)}")
    print()
    
    # Generate summary report
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in test_results if r['pass'])
    failed = sum(1 for r in test_results if not r['pass'])
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print()
    
    if failed > 0:
        print("FAILED TESTS:")
        for result in test_results:
            if not result['pass']:
                print(f"  ✗ {result['endpoint']} ({result['role']})")
                print(f"    Expected: {result['expected_status']}, Actual: {result['actual_status']}")
                if 'error' in result:
                    print(f"    Error: {result['error']}")
                if 'calculation_issues' in result:
                    print(f"    Calculation Issues: {result['calculation_issues']}")
        print()
    
    # Save detailed report to file
    with open('backend_audit_report.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed/total)*100,
            'results': test_results
        }, f, indent=2)
    
    print("Detailed report saved to: backend_audit_report.json")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
