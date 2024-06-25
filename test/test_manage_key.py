import unittest
from unittest.mock import Mock
from backend.Resource_test import ManageKey

class TestManageKey(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.manage_key = ManageKey(self.db)

    def test_generate_random_string(self):
        result = self.manage_key.generate_random_string()
        self.assertEqual(len(result), 200)

    def test_insert_key(self):
        self.manage_key.insert_key("random_key", 1)
        self.db.cursor.execute.assert_called_once_with(
            '''INSERT INTO `keys` (temp_key, user_id) VALUES (%s, %s)''', ("random_key", 1)
        )
        self.db.conn.commit.assert_called_once()

    def test_has_key(self):
        self.db.cursor.fetchone.return_value = (1,)
        result = self.manage_key.has_key("random_key")
        self.db.cursor.execute.assert_called_once_with(
            '''SELECT EXISTS(SELECT 1 FROM `keys` WHERE `temp_key` = %s)''', ("random_key",)
        )
        self.assertTrue(result)

    def test_whose_key(self):
        self.db.cursor.fetchone.return_value = (1,)
        result = self.manage_key.whose_key("random_key")
        self.db.cursor.execute.assert_called_once_with(
            '''SELECT user_id FROM `keys` WHERE `temp_key` = %s''', ("random_key",)
        )
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()
