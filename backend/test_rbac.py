import urllib.request
import json

def login(username, password):
    data = json.dumps({'username': username, 'password': password}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8001/api/v1/auth/login/', data=data, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    return result['access']

def test_endpoint(access_token, endpoint):
    req = urllib.request.Request(f'http://127.0.0.1:8001/api/v1{endpoint}', headers={'Authorization': f'Bearer {access_token}'})
    try:
        response = urllib.request.urlopen(req)
        return response.status
    except urllib.error.HTTPError as e:
        return e.code

print("RBAC Test Results")
print("=" * 50)

# Test 1: Student accessing student dashboard
print("\nTest 1: Student -> Student Dashboard")
student_token = login('student1', 'student123')
status = test_endpoint(student_token, '/student/dashboard/')
print(f"Actual: {status}, Expected: 200")
print(f"Result: {'PASSED' if status == 200 else 'FAILED'}")

# Test 2: Student accessing parent dashboard
print("\nTest 2: Student -> Parent Dashboard")
status = test_endpoint(student_token, '/parent/dashboard/')
print(f"Actual: {status}, Expected: 403")
print(f"Result: {'PASSED' if status == 403 else 'FAILED'}")

# Test 3: Parent accessing parent dashboard
print("\nTest 3: Parent -> Parent Dashboard")
parent_token = login('parent1', 'parent123')
status = test_endpoint(parent_token, '/parent/dashboard/')
print(f"Actual: {status}, Expected: 200")
print(f"Result: {'PASSED' if status == 200 else 'FAILED'}")

# Test 4: Parent accessing student dashboard
print("\nTest 4: Parent -> Student Dashboard")
status = test_endpoint(parent_token, '/student/dashboard/')
print(f"Actual: {status}, Expected: 403")
print(f"Result: {'PASSED' if status == 403 else 'FAILED'}")

# Test 5: Admin accessing admin dashboard
print("\nTest 5: Admin -> Admin Dashboard")
admin_token = login('admin', 'admin123')
status = test_endpoint(admin_token, '/admin/dashboard/')
print(f"Actual: {status}, Expected: 403")
print(f"Result: {'PASSED' if status == 403 else 'FAILED'}")
print("(Note: Admin role is separate from student/parent roles)")
