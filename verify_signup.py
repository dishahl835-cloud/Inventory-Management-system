import requests
import sys
import secrets

BASE_URL = 'http://127.0.0.1:5000'
SIGNUP_URL = f'{BASE_URL}/signup'
LOGIN_URL = f'{BASE_URL}/login'
API_URL = f'{BASE_URL}/api/products'

def test_signup():
    print("Testing User Registration...")
    
    # Generate random username
    username = f"newuser_{secrets.token_hex(4)}"
    password = "password123"
    print(f"Creating user: {username}")

    # 1. Test Signup
    session = requests.Session()
    resp = session.post(SIGNUP_URL, json={'username': username, 'password': password})
    if resp.status_code == 201:
        print("PASS: Signup successful.")
    else:
        print(f"FAIL: Signup failed. {resp.status_code} - {resp.text}")
        sys.exit(1)

    # 2. Test Login with New User
    print("Logging in with new user...")
    resp = session.post(LOGIN_URL, json={'username': username, 'password': password})
    if resp.status_code == 200 and resp.json()['role'] == 'user':
        print("PASS: Login successful and role is 'user'.")
    else:
        print(f"FAIL: Login failed. {resp.status_code}")
        sys.exit(1)

    # 3. Verify Read Access
    print("Verifying read access...")
    resp = session.get(API_URL)
    if resp.status_code == 200:
        print("PASS: Read access confirmed.")
    else:
        print(f"FAIL: Read access denied. {resp.status_code}")
        sys.exit(1)

    # 4. Verify Write Access Denied
    print("Verifying write access denied...")
    resp = session.post(API_URL, json={"name": "Fail", "category": "Fail", "quantity": 1, "price": 1})
    if resp.status_code == 403:
        print("PASS: Write access correctly denied.")
    else:
        print(f"FAIL: Write access allowed! {resp.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    test_signup()
