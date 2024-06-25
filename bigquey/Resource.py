from google.cloud import bigquery

class User:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name

    def create_user(self, username, password, email, role):
        query = f"""
            INSERT INTO `{self.table_name}` (username, password, email, role)
            VALUES ('{username}', '{password}', '{email}', '{role}')
        """
        self.client.query(query).result()

    def update_user(self, user_id, username=None, password=None, email=None, role=None):
        updates = []
        if username:
            updates.append(f"username = '{username}'")
        if password:
            updates.append(f"password = '{password}'")
        if email:
            updates.append(f"email = '{email}'")
        if role:
            updates.append(f"role = '{role}'")
        update_str = ", ".join(updates)
        query = f"UPDATE `{self.table_name}` SET {update_str} WHERE user_id = {user_id}"
        self.client.query(query).result()

    def delete_user(self, user_id):
        query = f"DELETE FROM `{self.table_name}` WHERE user_id = {user_id}"
        self.client.query(query).result()

    def list_users(self):
        query = f"SELECT * FROM `{self.table_name}`"
        results = self.client.query(query).result()
        return [dict(row) for row in results]


class Item:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name

    def create_item(self, item_name, price, item_description):
        query = f"""
            INSERT INTO `{self.table_name}` (item_name, price, item_description)
            VALUES ('{item_name}', {price}, '{item_description}')
        """
        self.client.query(query).result()

    def update_item(self, item_id, item_name=None, price=None, item_description=None):
        updates = []
        if item_name:
            updates.append(f"item_name = '{item_name}'")
        if price:
            updates.append(f"price = {price}")
        if item_description:
            updates.append(f"item_description = '{item_description}'")
        update_str = ", ".join(updates)
        query = f"UPDATE `{self.table_name}` SET {update_str} WHERE item_id = {item_id}"
        self.client.query(query).result()

    def delete_item(self, item_id):
        query = f"DELETE FROM `{self.table_name}` WHERE item_id = {item_id}"
        self.client.query(query).result()

    def list_items(self):
        query = f"SELECT * FROM `{self.table_name}`"
        results = self.client.query(query).result()
        return [dict(row) for row in results]


class Order:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name

    def create_order(self, user_id, item_id, item_amount):
        query = f"""
            INSERT INTO `{self.table_name}` (user_id, item_id, item_amount)
            VALUES ({user_id}, {item_id}, {item_amount})
        """
        self.client.query(query).result()

    def update_order(self, order_id, user_id=None, item_id=None, item_amount=None):
        updates = []
        if user_id:
            updates.append(f"user_id = {user_id}")
        if item_id:
            updates.append(f"item_id = {item_id}")
        if item_amount:
            updates.append(f"item_amount = {item_amount}")
        update_str = ", ".join(updates)
        query = f"UPDATE `{self.table_name}` SET {update_str} WHERE order_id = {order_id}"
        self.client.query(query).result()

    def delete_order(self, order_id):
        query = f"DELETE FROM `{self.table_name}` WHERE order_id = {order_id}"
        self.client.query(query).result()

    def list_orders(self, user_id=None):
        if user_id:
            query = f"SELECT * FROM `{self.table_name}` WHERE user_id = {user_id}"
        else:
            query = f"SELECT * FROM `{self.table_name}`"
        results = self.client.query(query).result()
        return [dict(row) for row in results]


import string
import random

class ManageKey:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name

    def generate_random_string(self, length=200):
        characters = string.ascii_letters + string.digits + string.punctuation
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def insert_key(self, temp_key, user_id):
        query = f"""
            INSERT INTO `{self.table_name}` (temp_key, user_id)
            VALUES ('{temp_key}', {user_id})
        """
        self.client.query(query).result()

    def has_key(self, key):
        query = f"SELECT EXISTS(SELECT 1 FROM `{self.table_name}` WHERE temp_key = '{key}')"
        result = list(self.client.query(query).result())
        return result[0][0] == 1

    def whose_key(self, key):
        query = f"SELECT user_id FROM `{self.table_name}` WHERE temp_key = '{key}'"
        result = list(self.client.query(query).result())
        return result[0][0] if result else None
