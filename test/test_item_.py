import unittest
from unittest.mock import Mock
from backend.Resource_test import Item

class TestItem(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.item = Item(self.db)

    def test_create_item(self):
        self.item.create_item("Laptop", 999.99, "A high-performance laptop.")
        self.db.cursor.execute.assert_called_once_with(
            '''INSERT INTO Item (item_name, price, item_description) VALUES (%s, %s, %s)''',
            ("Laptop", 999.99, "A high-performance laptop.")
        )
        self.db.conn.commit.assert_called_once()

    def test_update_item(self):
        self.item.update_item(1, item_name="Desktop")
        self.db.cursor.execute.assert_called_once_with(
            '''UPDATE Item SET item_name = %s WHERE item_id = %s''', ("Desktop", 1)
        )
        self.db.conn.commit.assert_called_once()

    def test_delete_item(self):
        self.item.delete_item(1)
        self.db.cursor.execute.assert_called_once_with('''DELETE FROM Item WHERE item_id = %s''', (1,))
        self.db.conn.commit.assert_called_once()

    def test_list_items(self):
        self.db.cursor.fetchall.return_value = [("Laptop", 999.99, "A high-performance laptop.")]
        result = self.item.list_items()
        self.db.cursor.execute.assert_called_once_with('''SELECT * FROM Item''')
        self.assertEqual(result, [("Laptop", 999.99, "A high-performance laptop.")])

if __name__ == '__main__':
    unittest.main()
