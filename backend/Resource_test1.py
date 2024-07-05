import mysql.connector
import string
import random
import json
import redis
from passlib.hash import bcrypt
#import bcrypt
import os
import secrets 

class Database:
    def __init__(self, host='mysql', user='root', password='sayan123', port=3306, database='pesto'):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS User (
                                user_id INT AUTO_INCREMENT PRIMARY KEY,
                                username VARCHAR(50) NOT NULL,
                                password VARCHAR(255) NOT NULL,
                                email VARCHAR(100) NOT NULL,
                                role VARCHAR(50) NOT NULL DEFAULT 'user')
                               ''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Item (
                               item_id INT AUTO_INCREMENT PRIMARY KEY,
                               item_name VARCHAR(100) NOT NULL,
                               price DECIMAL(10, 2) NOT NULL,
                               item_description TEXT)
                               ''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS `Order` (
                               order_id INT AUTO_INCREMENT PRIMARY KEY,
                               user_id INT NOT NULL,
                               item_id INT NOT NULL,
                               item_amount INT NOT NULL,
                               FOREIGN KEY (user_id) REFERENCES User(user_id),
                               FOREIGN KEY (item_id) REFERENCES Item(item_id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS `keys` (
                               temp_key VARCHAR(255) NOT NULL,
                               user_id INT NOT NULL,
                               create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               PRIMARY KEY (temp_key),
                               FOREIGN KEY (user_id) REFERENCES User(user_id))''')
        self.conn.commit()

    def get_lock(self, lock_name):
        self.cursor.execute(f"SELECT GET_LOCK('{lock_name}', 10)")
        result = self.cursor.fetchone()
        return result[0] == 1

    def release_lock(self, lock_name):
        self.cursor.execute(f"SELECT RELEASE_LOCK('{lock_name}')")
        result = self.cursor.fetchone()
        return result[0] == 1

class User:
    def __init__(self, db):
        self.db = db

    def create_user(self, username, password, email, role='user'):
        fixed_salt = 'abcdefghijklmonopqrstu'
        password = bcrypt.using(salt=fixed_salt).hash(password)
        lock_name = f"user_create" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''INSERT INTO User (username, password, email, role) VALUES (%s, %s, %s, %s)''', (username, password, email, role))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def update_user(self, user_id, username=None, password=None, email=None, role=None):
        lock_name = f"user_update" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                if username:
                    self.db.cursor.execute('''UPDATE User SET username = %s WHERE user_id = %s''', (username, user_id))
                if password:
                    hashed_password = bcrypt.hash(password)
                    self.db.cursor.execute('''UPDATE User SET password = %s WHERE user_id = %s''', (hashed_password, user_id))
                if email:
                    self.db.cursor.execute('''UPDATE User SET email = %s WHERE user_id = %s''', (email, user_id))
                if role:
                    self.db.cursor.execute('''UPDATE User SET role = %s WHERE user_id = %s''', (role, user_id))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def delete_user(self, user_id):
        lock_name = f"user_delete" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''DELETE FROM User WHERE user_id = %s''', (user_id,))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def list_users(self):
        self.db.cursor.execute('''SELECT * FROM User''')
        return self.db.cursor.fetchall()

class Item:
    def __init__(self, db):
        self.db = db

    def create_item(self, item_name, price, item_description):
        lock_name = f"item_create" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''INSERT INTO Item (item_name, price, item_description) VALUES (%s, %s, %s)''', (item_name, price, item_description))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def update_item(self, item_id, item_name=None, price=None, item_description=None):
        lock_name = f"item_update" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                if item_name:
                    self.db.cursor.execute('''UPDATE Item SET item_name = %s WHERE item_id = %s''', (item_name, item_id))
                if price:
                    self.db.cursor.execute('''UPDATE Item SET price = %s WHERE item_id = %s''', (price, item_id))
                if item_description:
                    self.db.cursor.execute('''UPDATE Item SET item_description = %s WHERE item_id = %s''', (item_description, item_id))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def delete_item(self, item_id):
        lock_name = f"item_delete" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''DELETE FROM Item WHERE item_id = %s''', (item_id,))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def list_items(self):
        self.db.cursor.execute('''SELECT * FROM Item''')
        return self.db.cursor.fetchall()

class Order:
    def __init__(self, db):
        self.db = db
        self.redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

    def create_order(self, user_id, item_id, item_amount):
        lock_name = f"order_create" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''INSERT INTO `Order` (user_id, item_id, item_amount) VALUES (%s, %s, %s)''', (user_id, item_id, item_amount))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def create_order_asynchronous(self, user_id, item_id, item_amount):
        order_data = {
            'user_id': user_id,
            'item_id': item_id,
            'item_amount': item_amount
        }
        self.redis_client.rpush('order_queue', json.dumps(order_data))

    def update_order(self, order_id, user_id=None, item_id=None, item_amount=None):
        lock_name = f"order_update" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                if user_id:
                    self.db.cursor.execute('''UPDATE `Order` SET user_id = %s WHERE order_id = %s''', (user_id, order_id))
                if item_id:
                    self.db.cursor.execute('''UPDATE `Order` SET item_id = %s WHERE order_id = %s''', (item_id, order_id))
                if item_amount:
                    self.db.cursor.execute('''UPDATE `Order` SET item_amount = %s WHERE order_id = %s''', (item_amount, order_id))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def delete_order(self, order_id):
        lock_name = f"order_delete" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''DELETE FROM `Order` WHERE order_id = %s''', (order_id,))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def list_orders(self, user_id=None):
        if user_id:
            self.db.cursor.execute('''SELECT * FROM `Order` WHERE user_id = %s''', (user_id,))
        else:
            self.db.cursor.execute('''SELECT * FROM `Order`''')
        return self.db.cursor.fetchall()

class ManageKey:
    def __init__(self, db):
        self.db = db

    def generate_random_string(self, length=200):
        characters = string.ascii_letters + string.digits + string.punctuation
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def insert_key(self, temp_key, user_id):
        lock_name = f"key_insert" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''INSERT INTO `keys` (temp_key, user_id) VALUES (%s, %s)''', (temp_key, user_id))
                self.db.conn.commit()
            finally:
                self.db.release_lock(lock_name)

    def has_key(self, key):
        lock_name = f"key_check" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''SELECT EXISTS(SELECT 1 FROM `keys` WHERE `temp_key` = %s)''', (key,))
                result = self.db.cursor.fetchone()
                return result[0] == 1
            finally:
                self.db.release_lock(lock_name)

    def whose_key(self, key):
        lock_name = f"key_user" + secrets.token_hex(nbytes=16)
        if self.db.get_lock(lock_name):
            try:
                self.db.cursor.execute('''SELECT user_id FROM `keys` WHERE `temp_key` = %s''', (key,))
                result = self.db.cursor.fetchone()
                return result[0] if result else None
            finally:
                self.db.release_lock(lock_name)

# Usage example
db = Database()
user = User(db)
item = Item(db)
order = Order(db)

# Create entities
user.create_user("john_doe", "password123", "john@example.com", "admin")
item.create_item("Laptop", 999.99, "A high-performance laptop.")
order.create_order(1, 1, 2)

# List entities
print(user.list_users())
print(item.list_items())
print(order.list_orders(1))

manager = ManageKey(db)
random_key = manager.generate_random_string()
manager.insert_key(random_key, 1)  # Assuming user_id 1 exists
print(f"Inserted key: {random_key}")

# Check if the key exists
key_exists = manager.has_key(random_key)
print(f"Key exists: {key_exists}")

# Get user_id for the key
user_id_for_key = manager.whose_key(random_key)
print(f"User ID for key: {user_id_for_key}")

order.create_order_asynchronous(1, 1, 5)
