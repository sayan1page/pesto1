from flask import Flask, request, jsonify
from flask_cors import CORS
from Resource_test1 import Database, User, Item, Order, ManageKey
import redis
import json
#import bcrypt
from passlib.hash import bcrypt

app = Flask(__name__)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})

# Initialize database and classes
db = Database()
user = User(db)
item = Item(db)
order = Order(db)
key_manager = ManageKey(db)

# Initialize Redis client
redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

# Helper function to check if a key is valid
def is_authenticated(key):
    return key_manager.has_key(key)

# Helper function to check if a user is admin
def is_admin(user_id):
    user_data = user.list_users()
    for u in user_data:
        if u[0] == user_id and u[4] == 'admin':
            return True
    return False

# Endpoint to create a user
@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'user')
        user.create_user(username, password, email, role)
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to create an item
@app.route('/create_item', methods=['POST'])
def create_item():
    try:
        key = request.headers.get('Authorization')
        if not is_authenticated(key):
            return jsonify({"message": "Unauthorized"}), 401
        user_id = key_manager.whose_key(key)
        if not is_admin(user_id):
            return jsonify({"message": "Unauthorized"}), 401
        data = request.get_json()
        item_name = data.get('item_name')
        price = data.get('price')
        item_description = data.get('item_description')
        item.create_item(item_name, price, item_description)
        return jsonify({"message": "Item created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to authenticate a user and generate a key
@app.route('/authenticate_user', methods=['POST'])
def authenticate_user():
    try:
        data = request.get_json()
        username = data.get('username')
        fixed_salt = 'abcdefghijklmonopqrstu'
        password = bcrypt.using(salt=fixed_salt).hash(data.get('password'))
        user_data = user.list_users()
        for u in user_data:
            if u[1] == username and u[2] == password:
                key = key_manager.generate_random_string()
                key_manager.insert_key(key, u[0])
                return jsonify({"key": key}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to delete a user
@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    try:
        key = request.headers.get('Authorization')
        if not is_authenticated(key):
            return jsonify({"message": "Unauthorized"}), 401
        user_id = key_manager.whose_key(key)
        user.delete_user(user_id)
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to update a user's email
@app.route('/update_user_email', methods=['PUT'])
def update_user_email():
    try:
        key = request.headers.get('Authorization')
        if not is_authenticated(key):
            return jsonify({"message": "Unauthorized"}), 401
        data = request.get_json()
        new_email = data.get('email')
        user_id = key_manager.whose_key(key)
        user.update_user(user_id, email=new_email)
        return jsonify({"message": "Email updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to update a user's password
@app.route('/update_user_password', methods=['PUT'])
def update_user_password():
    try:
        key = request.headers.get('Authorization')
        if not is_authenticated(key):
            return jsonify({"message": "Unauthorized"}), 401
        data = request.get_json()
        new_password = data.get('password')
        user_id = key_manager.whose_key(key)
        user.update_user(user_id, password=new_password)
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to create an order
@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        key = request.headers.get('Authorization')
        if not is_authenticated(key):
            return jsonify({"message": "Unauthorized"}), 401
        data = request.get_json()
        item_id = data.get('item_id')
        item_amount = data.get('item_amount')
        user_id = key_manager.whose_key(key)
        order.create_order(user_id, item_id, item_amount)
        return jsonify({"message": "Order created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to create an order asynchronously
@app.route('/create_order_asynchronous', methods=['POST'])
def create_order_asynchronous():
    try:
        key = request.headers.get('Authorization')
        if not is_authenticated(key):
            return jsonify({"message": "Unauthorized"}), 401
        data = request.get_json()
        item_id = data.get('item_id')
        item_amount = data.get('item_amount')
        user_id = key_manager.whose_key(key)
        order.create_order_asynchronous(user_id, item_id, item_amount)
        return jsonify({"message": "Order published to queue successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to list orders for a user
@app.route('/list_orders', methods=['GET'])
def list_orders():
    try:
        key = request.headers.get('Authorization')
        if not is_authenticated(key):
            return jsonify({"message": "Unauthorized"}), 401
        user_id = key_manager.whose_key(key)
        
        # Check if orders are cached
        cache_key = f"orders_user_{user_id}"
        cached_orders = redis_client.get(cache_key)
        
        if cached_orders:
            orders = json.loads(cached_orders)
        else:
            orders = order.list_orders(user_id)
            redis_client.setex(cache_key, 60, json.dumps(orders))  # Cache for 60 sec
        
        res = []
        for o in orders:
            temp = {}
            temp['order_id'] = o[0]
            temp['user_id'] = o[1]
            temp['item_id'] = o[2]
            temp['item_amount'] = o[3]
            res.append(temp)        
        return jsonify({"orders": res}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
