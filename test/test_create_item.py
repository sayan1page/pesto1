import unittest
from unittest.mock import patch, Mock
from backend.app import app

class TestCreateItem(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('backend.app.is_authenticated')
    @patch('backend.app.key_manager')
    @patch('backend.app.is_admin')
    @patch('backend.app.item')
    def test_create_item_success(self, mock_item, mock_is_admin, mock_key_manager, mock_is_authenticated):
        # Mock the key_manager and is_authenticated to return True
        mock_is_authenticated.return_value = True
        mock_key_manager.whose_key.return_value = 1
        mock_is_admin.return_value = True

        # Mock the create_item method
        mock_item.create_item.return_value = None

        # Make a POST request to the /create_item endpoint
        response = self.app.post('/create_item', headers={'Authorization': 'valid_key'}, json={
            'item_name': 'Laptop',
            'price': 999.99,
            'item_description': 'A high-performance laptop.'
        })

        # Assert the response status code and message
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'message': 'Item created successfully'})

    @patch('backend.app.is_authenticated')
    @patch('backend.app.key_manager')
    @patch('backend.app.is_admin')
    @patch('backend.app.item')
    def test_create_item_unauthorized(self, mock_item, mock_is_admin, mock_key_manager, mock_is_authenticated):
        # Mock the key_manager and is_authenticated to return True
        mock_is_authenticated.return_value = True
        mock_key_manager.whose_key.return_value = 1
        mock_is_admin.return_value = False

        # Make a POST request to the /create_item endpoint
        response = self.app.post('/create_item', headers={'Authorization': 'valid_key'}, json={
            'item_name': 'Laptop',
            'price': 999.99,
            'item_description': 'A high-performance laptop.'
        })

        # Assert the response status code and message
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'message': 'Unauthorized'})

    @patch('backend.app.is_authenticated')
    @patch('backend.app.key_manager')
    @patch('backend.app.is_admin')
    @patch('backend.app.item')
    def test_create_item_invalid_key(self, mock_item, mock_is_admin, mock_key_manager, mock_is_authenticated):
        # Mock the key_manager and is_authenticated to return False
        mock_is_authenticated.return_value = False

        # Make a POST request to the /create_item endpoint
        response = self.app.post('/create_item', headers={'Authorization': 'invalid_key'}, json={
            'item_name': 'Laptop',
            'price': 999.99,
            'item_description': 'A high-performance laptop.'
        })

        # Assert the response status code and message
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'message': 'Unauthorized'})

if __name__ == '__main__':
    unittest.main()
