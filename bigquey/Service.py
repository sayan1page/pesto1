from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import bigquery
from Resource import User, Item, Order, ManageKey
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Ensure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_your_service_account_file.json"

# Initialize BigQuery client
client = bigquery.Client()

# Replace with your dataset and table names
DATASET_ID = "your_dataset_id"
USER_TABLE = f"{DATASET_ID}.User"
ITEM_TABLE = f"{DATASET_ID}.Item"
ORDER_TABLE = f"{DATASET_ID}.Order"
KEYS_TABLE = f"{DATASET_ID}.keys"

# Initialize classes
user = User(client, USER_TABLE)
item = Item(client, ITEM_TABLE)
order = Order(client, ORDER_TABLE)
key_manager = ManageKey(client, KEYS_TABLE)

# Helper function to check if a key is valid
def is_authenticated(key):
    return key_manager.has_key(key)

# Endpoint to create a user
@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')
    user.create_user(username, password, email, role)
    return jsonify({"message": "User created successfully"}), 201

# Endpoint to create an item
@app.route('/create_item', methods=['POST'])
def create_item():
    data = request.get_json()
    item_name = data.get('item_name')
    price = data.get('price')
    item_description = data.get('item_description')
    item.create_item(item_name, price, item_description)
    return jsonify({"message": "Item created successfully"}), 201

# Endpoint to authenticate a user and generate a key
@app.route('/authenticate_user', methods=['POST'])
def authenticate_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    user_data = user.list_users()
    for u in user_data:
        if u['username'] == username and u['password'] == password and u['email'] == email:
            key = key_manager.generate_random_string()
            key_manager.insert_key(key, u['user_id'])
            return jsonify({"key": key}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# Endpoint to delete a user
@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    key = request.headers.get('Authorization')
    if not is_authenticated(key):
        return jsonify({"message": "Unauthorized"}), 401
    user_id = key_manager.whose_key(key)
    user.delete_user(user_id)
    return jsonify({"message": "User deleted successfully"}), 200

# Endpoint to update a user's email
@app.route('/update_user_email', methods=['PUT'])
def update_user_email():
    key = request.headers.get('Authorization')
    if not is_authenticated(key):
        return jsonify({"message": "Unauthorized"}), 401
    data = request.get_json()
    new_email = data.get('email')
    user_id = key_manager.whose_key(key)
    user.update_user(user_id, email=new_email)
    return jsonify({"message": "Email updated successfully"}), 200

# Endpoint to update a user's password
@app.route('/update_user_password', methods=['PUT'])
def update_user_password():
    key = request.headers.get('Authorization')
    if not is_authenticated(key):
        return jsonify({"message": "Unauthorized"}), 401
    data = request.get_json()
    new_password = data.get('password')
    user_id = key_manager.whose_key(key)
    user.update_user(user_id, password=new_password)
    return jsonify({"message": "Password updated successfully"}), 200

# Endpoint to create an order
@app.route('/create_order', methods=['POST'])
def create_order():
    key = request.headers.get('Authorization')
    if not is_authenticated(key):
        return jsonify({"message": "Unauthorized"}), 401
    data = request.get_json()
    item_id = data.get('item_id')
    item_amount = data.get('item_amount')
    user_id = key_manager.whose_key(key)
    order.create_order(user_id, item_id, item_amount)
    return jsonify({"message": "Order created successfully"}), 201

# Endpoint to list orders for a user
@app.route('/list_orders', methods=['GET'])
def list_orders():
    key = request.headers.get('Authorization')
    if not is_authenticated(key):
        return jsonify({"message": "Unauthorized"}), 401
    
    user_id = key_manager.whose_key(key)
    if user_id is None:
        return jsonify({"message": "Unauthorized"}), 401
    
    orders = order.list_orders(user_id)
    res = []
    for o in orders:
        temp = {
            'order_id': o['order_id'],
            'user_id': o['user_id'],
            'item_id': o['item_id'],
            'item_amount': o['item_amount']
        }
        res.append(temp)
    return jsonify({"orders": res}), 200

if __name__ == '__main__':
    app.run(debug=True)
