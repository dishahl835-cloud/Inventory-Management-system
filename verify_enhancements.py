import requests
import sys

BASE_URL = 'http://127.0.0.1:5000'
LOGIN_URL = f'{BASE_URL}/login'
API_URL = f'{BASE_URL}/api/products'
TRANS_URL = f'{BASE_URL}/api/transactions'

def test_enhancements():
    print("Testing System Enhancements...")
    
    session = requests.Session()
    # Login
    session.post(LOGIN_URL, json={'username': 'admin', 'password': 'admin123'})

    # 1. Trigger Transaction (Add Product)
    print("1. Triggering Transaction (Add Product)...")
    new_product = {"name": "Chart Test", "category": "Test", "quantity": 50, "price": 100.0}
    resp = session.post(API_URL, json=new_product)
    if resp.status_code != 201:
        print("FAIL: Could not add product.")
        sys.exit(1)

    # 2. Verify Transaction Log
    print("2. Verifying Transaction Log...")
    resp = session.get(TRANS_URL)
    transactions = resp.json()
    if len(transactions) > 0 and transactions[0]['type'] == 'IN' and transactions[0]['quantity'] == 50:
        print("PASS: Transaction logged correctly.")
    else:
        print(f"FAIL: Transaction not found. {transactions}")
        sys.exit(1)

    print("PASS: All backend enhancements verified.")

if __name__ == "__main__":
    test_enhancements()
