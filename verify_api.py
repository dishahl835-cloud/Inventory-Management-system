import requests
import time
import sys

BASE_URL = 'http://127.0.0.1:5000/api/products'

def test_api():
    print("Waiting for server to start...")
    time.sleep(3)

    # 1. Add Product
    print("Testing POST /api/products...")
    new_product = {
        "name": "Test Item",
        "category": "Test Category",
        "quantity": 10,
        "price": 99.99
    }
    try:
        response = requests.post(BASE_URL, json=new_product)
        if response.status_code == 201:
            print("PASS: Product added.")
        else:
            print(f"FAIL: Add product failed. Status: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"FAIL: Could not connect to server. {e}")
        sys.exit(1)

    # 2. Get Products
    print("Testing GET /api/products...")
    response = requests.get(BASE_URL)
    products = response.json()
    if len(products) > 0 and products[-1]['name'] == "Test Item":
        print("PASS: Product list retrieved.")
        product_id = products[-1]['id']
    else:
        print("FAIL: Product not found in list.")
        sys.exit(1)

    # 3. Update Product
    print(f"Testing PUT /api/products/{product_id}...")
    updated_product = new_product.copy()
    updated_product['quantity'] = 20
    response = requests.put(f"{BASE_URL}/{product_id}", json=updated_product)
    if response.status_code == 200:
        print("PASS: Product updated.")
    else:
        print(f"FAIL: Update failed. Status: {response.status_code}")

    # 4. Delete Product
    print(f"Testing DELETE /api/products/{product_id}...")
    response = requests.delete(f"{BASE_URL}/{product_id}")
    if response.status_code == 200:
        print("PASS: Product deleted.")
    else:
        print(f"FAIL: Delete failed. Status: {response.status_code}")

if __name__ == "__main__":
    test_api()
