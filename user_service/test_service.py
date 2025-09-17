import requests
import json

BASE_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")

def test_register():
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/users/register", json=user_data)
    print(f"Register: {response.status_code} - {response.json()}")
    return response.json().get('user', {}).get('id')

def test_login():
    """Test user login"""
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/users/login", json=login_data)
    print(f"Login: {response.status_code} - {response.json()}")
    return response.json().get('user', {}).get('id')

def test_profile(user_id):
    """Test get user profile"""
    response = requests.get(f"{BASE_URL}/api/users/profile/{user_id}")
    print(f"Profile: {response.status_code} - {response.json()}")

def test_list_users():
    """Test list all users"""
    response = requests.get(f"{BASE_URL}/api/users")
    print(f"List Users: {response.status_code} - {response.json()}")

if __name__ == "__main__":
    print("Testing User Service...")
    print("-" * 40)
    
    try:
        test_health()
        user_id = test_register()
        if user_id:
            test_profile(user_id)
        test_login()
        test_list_users()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to user service. Make sure it's running on port 5001")
