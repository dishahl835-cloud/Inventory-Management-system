from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import get_db_connection, init_db
import secrets
import sqlite3

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize DB on startup
init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', role=session.get('role'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return jsonify({'message': 'Login successful', 'role': user['role']})
        
        return jsonify({'message': 'Invalid credentials'}), 401
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/products', methods=['GET'])
def get_products():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
        
    new_product = request.get_json()
    name = new_product['name']
    category = new_product['category']
    quantity = new_product['quantity']
    price = new_product['price']

    conn = get_db_connection()
    cursor = conn.execute('INSERT INTO products (name, category, quantity, price) VALUES (?, ?, ?, ?)',
                 (name, category, quantity, price))
    product_id = cursor.lastrowid
    
    # Log Transaction
    conn.execute('INSERT INTO transactions (product_id, product_name, type, quantity) VALUES (?, ?, ?, ?)',
                 (product_id, name, 'IN', quantity))
                 
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
        
    updated_product = request.get_json()
    name = updated_product['name']
    category = updated_product['category']
    quantity = updated_product['quantity']
    price = updated_product['price']

    conn = get_db_connection()
    
    # Check previous quantity for logging
    old_prod = conn.execute('SELECT quantity FROM products WHERE id = ?', (id,)).fetchone()
    if old_prod:
        diff = quantity - old_prod['quantity']
        if diff != 0:
            type_ = 'IN' if diff > 0 else 'OUT'
            conn.execute('INSERT INTO transactions (product_id, product_name, type, quantity) VALUES (?, ?, ?, ?)',
                         (id, name, type_, abs(diff)))

    conn.execute('UPDATE products SET name = ?, category = ?, quantity = ?, price = ? WHERE id = ?',
                 (name, category, quantity, price, id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    prod = conn.execute('SELECT name, quantity FROM products WHERE id = ?', (id,)).fetchone()
    if prod:
        conn.execute('INSERT INTO transactions (product_id, product_name, type, quantity) VALUES (?, ?, ?, ?)',
                     (id, prod['name'], 'OUT', prod['quantity']))
                     
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in transactions])

if __name__ == '__main__':
    app.run(debug=True)
