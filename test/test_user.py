import unittest
from unittest.mock import Mock
from backend.Resource_test import User

class TestUser(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.user = User(self.db)

    def test_create_user(self):
        self.user.create_user("john_doe", "password123", "john@example.com", "admin")
        self.db.cursor.execute.assert_called_once_with(
            '''INSERT INTO User (username, password, email, role) VALUES (%s, %s, %s, %s)''',
            ("john_doe", "password123", "john@example.com", "admin")
        )
        self.db.conn.commit.assert_called_once()

    def test_update_user(self):
        self.user.update_user(1, username="jane_doe")
        self.db.cursor.execute.assert_called_once_with(
            '''UPDATE User SET username = %s WHERE user_id = %s''', ("jane_doe", 1)
        )
        self.db.conn.commit.assert_called_once()

    def test_delete_user(self):
        self.user.delete_user(1)
        self.db.cursor.execute.assert_called_once_with('''DELETE FROM User WHERE user_id = %s''', (1,))
        self.db.conn.commit.assert_called_once()

    def test_list_users(self):
        self.db.cursor.fetchall.return_value = [("john_doe", "password123", "john@example.com", "admin")]
        result = self.user.list_users()
        self.db.cursor.execute.assert_called_once_with('''SELECT * FROM User''')
        self.assertEqual(result, [("john_doe", "password123", "john@example.com", "admin")])

if __name__ == '__main__':
    unittest.main()
