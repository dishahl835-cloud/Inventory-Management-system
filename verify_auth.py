import requests
import sys

BASE_URL = 'http://127.0.0.1:5000'
API_URL = f'{BASE_URL}/api/products'
LOGIN_URL = f'{BASE_URL}/login'

def test_auth():
    print("Testing Authentication & Roles...")

    # 1. Test Login (Admin)
    print("1. Login as Admin...")
    session_admin = requests.Session()
    resp = session_admin.post(LOGIN_URL, json={'username': 'admin', 'password': 'admin123'})
    if resp.status_code == 200 and resp.json()['role'] == 'admin':
        print("PASS: Admin login successful.")
    else:
        print(f"FAIL: Admin login failed. {resp.status_code}")
        sys.exit(1)

    # 2. Test Login (User)
    print("2. Login as User...")
    session_user = requests.Session()
    resp = session_user.post(LOGIN_URL, json={'username': 'user', 'password': 'user123'})
    if resp.status_code == 200 and resp.json()['role'] == 'user':
        print("PASS: User login successful.")
    else:
        print(f"FAIL: User login failed. {resp.status_code}")
        sys.exit(1)

    # 3. Test Admin Access (Create Product)
    print("3. Test Admin Create Product...")
    new_product = {"name": "Auth Test", "category": "Test", "quantity": 5, "price": 10.0}
    resp = session_admin.post(API_URL, json=new_product)
    if resp.status_code == 201:
        print("PASS: Admin created product.")
    else:
        print(f"FAIL: Admin create failed. {resp.status_code}")
        sys.exit(1)

    # 4. Test User Access (Create Product - Should Fail)
    print("4. Test User Create Product (Should Fail)...")
    resp = session_user.post(API_URL, json=new_product)
    if resp.status_code == 403:
        print("PASS: User blocked from creating product.")
    else:
        print(f"FAIL: User was able to create product! {resp.status_code}")
        sys.exit(1)

    # 5. Test User Access (Read Products - Should Pass)
    print("5. Test User Read Products...")
    resp = session_user.get(API_URL)
    if resp.status_code == 200:
        print("PASS: User can read products.")
    else:
        print(f"FAIL: User read failed. {resp.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    test_auth()
