import unittest
from unittest.mock import patch, Mock
from backend.app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('backend.app.user')
    def test_create_user(self, mock_user):
        mock_user.create_user.return_value = None
        response = self.app.post('/create_user', json={
            "username": "john_doe",
            "password": "password123",
            "email": "john@example.com",
            "role": "admin"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "User created successfully"})

    

    @patch('backend.app.user')
    @patch('backend.app.key_manager')
    def test_authenticate_user(self, mock_key_manager, mock_user):
        mock_user.list_users.return_value = [(1, "john_doe", "password123", "john@example.com", "admin")]
        mock_key_manager.generate_random_string.return_value = "random_key"
        mock_key_manager.insert_key.return_value = None

        response = self.app.post('/authenticate_user', json={
            "username": "john_doe",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"key": "random_key"})

    @patch('backend.app.user')
    @patch('backend.app.key_manager')
    def test_delete_user(self, mock_key_manager, mock_user):
        mock_key_manager.has_key.return_value = True
        mock_key_manager.whose_key.return_value = 1
        mock_user.delete_user.return_value = None

        response = self.app.delete('/delete_user', headers={"Authorization": "random_key"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "User deleted successfully"})

    @patch('backend.app.user')
    @patch('backend.app.key_manager')
    def test_update_user_email(self, mock_key_manager, mock_user):
        mock_key_manager.has_key.return_value = True
        mock_key_manager.whose_key.return_value = 1
        mock_user.update_user.return_value = None

        response = self.app.put('/update_user_email', headers={"Authorization": "random_key"}, json={
            "email": "new_email@example.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Email updated successfully"})

    @patch('backend.app.user')
    @patch('backend.app.key_manager')
    def test_update_user_password(self, mock_key_manager, mock_user):
        mock_key_manager.has_key.return_value = True
        mock_key_manager.whose_key.return_value = 1
        mock_user.update_user.return_value = None

        response = self.app.put('/update_user_password', headers={"Authorization": "random_key"}, json={
            "password": "new_password"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Password updated successfully"})

    @patch('backend.app.order')
    @patch('backend.app.key_manager')
    def test_create_order(self, mock_key_manager, mock_order):
        mock_key_manager.has_key.return_value = True
        mock_key_manager.whose_key.return_value = 1
        mock_order.create_order.return_value = None

        response = self.app.post('/create_order', headers={"Authorization": "random_key"}, json={
            "item_id": 1,
            "item_amount": 2
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "Order created successfully"})

    @patch('backend.app.order')
    @patch('backend.app.key_manager')
    def test_list_orders(self, mock_key_manager, mock_order):
        mock_key_manager.has_key.return_value = True
        mock_key_manager.whose_key.return_value = 1
        mock_order.list_orders.return_value = [
            (1, 1, 1, 2),
            (2, 1, 2, 1)
        ]

        response = self.app.get('/list_orders', headers={"Authorization": "random_key"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "orders": [
                {"order_id": 1, "user_id": 1, "item_id": 1, "item_amount": 2},
                {"order_id": 2, "user_id": 1, "item_id": 2, "item_amount": 1}
            ]
        })

if __name__ == '__main__':
    unittest.main()
