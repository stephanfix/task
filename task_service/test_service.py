import requests
import json
import time

TASK_SERVICE_URL = "http://localhost:5002"
USER_SERVICE_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{TASK_SERVICE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")

def create_test_user():
    """Create a test user for task testing"""
    user_data = {
        "username": "taskuser",
        "email": "taskuser@example.com",
        "password": "password123"
    }
    response = requests.post(f"{USER_SERVICE_URL}/api/users/register", json=user_data)
    if response.status_code == 201:
        return response.json().get('user', {}).get('id')
    else:
        # User might already exist, try to login
        login_data = {
            "username": "taskuser",
            "password": "password123"
        }
        response = requests.post(f"{USER_SERVICE_URL}/api/users/login", json=login_data)
        if response.status_code == 200:
            return response.json().get('user', {}).get('id')
    return None

def test_create_task(user_id):
    """Test task creation"""
    task_data = {
        "user_id": user_id,
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the microservices project",
        "status": "pending",
        "priority": "high",
        "due_date": "2025-12-31T23:59:59"
    }
    response = requests.post(f"{TASK_SERVICE_URL}/api/tasks", json=task_data)
    print(f"Create Task: {response.status_code} - {response.json()}")
    return response.json().get('task', {}).get('id') if response.status_code == 201 else None

def test_get_tasks(user_id):
    """Test getting tasks for a user"""
    response = requests.get(f"{TASK_SERVICE_URL}/api/tasks", params={"user_id": user_id})
    print(f"Get Tasks: {response.status_code} - {response.json()}")

def test_get_task(task_id):
    """Test getting a specific task"""
    response = requests.get(f"{TASK_SERVICE_URL}/api/tasks/{task_id}")
    print(f"Get Task: {response.status_code} - {response.json()}")

def test_update_task(task_id):
    """Test updating a task"""
    update_data = {
        "status": "in_progress",
        "description": "Updated description - work in progress"
    }
    response = requests.put(f"{TASK_SERVICE_URL}/api/tasks/{task_id}", json=update_data)
    print(f"Update Task: {response.status_code} - {response.json()}")

def test_task_stats(user_id):
    """Test task statistics"""
    response = requests.get(f"{TASK_SERVICE_URL}/api/tasks/stats/{user_id}")
    print(f"Task Stats: {response.status_code} - {response.json()}")

def test_delete_task(task_id):
    """Test deleting a task"""
    response = requests.delete(f"{TASK_SERVICE_URL}/api/tasks/{task_id}")
    print(f"Delete Task: {response.status_code} - {response.json()}")

if __name__ == "__main__":
    print("Testing Task Service...")
    print("-" * 50)
    
    try:
        # Test health
        test_health()
        
        # Create or get test user
        user_id = create_test_user()
        if not user_id:
            print("Error: Could not create/find test user")
            exit(1)
        
        print(f"Using test user ID: {user_id}")
        
        # Test task operations
        task_id = test_create_task(user_id)
        if task_id:
            test_get_task(task_id)
            test_update_task(task_id)
            test_get_tasks(user_id)
            test_task_stats(user_id)
            
            # Uncomment to test deletion
            # test_delete_task(task_id)
        
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to services. Make sure both User Service (port 5001) and Task Service (port 5002) are running")
        print(f"Connection error: {e}")
