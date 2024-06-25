import unittest
from unittest.mock import Mock
from backend.Resource_test import Order

class TestOrder(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.order = Order(self.db)

    def test_create_order(self):
        self.order.create_order(1, 1, 2)
        self.db.cursor.execute.assert_called_once_with(
            '''INSERT INTO `Order` (user_id, item_id, item_amount) VALUES (%s, %s, %s)''',
            (1, 1, 2)
        )
        self.db.conn.commit.assert_called_once()

    def test_update_order(self):
        self.order.update_order(1, item_amount=5)
        self.db.cursor.execute.assert_called_once_with(
            '''UPDATE `Order` SET item_amount = %s WHERE order_id = %s''', (5, 1)
        )
        self.db.conn.commit.assert_called_once()

    def test_delete_order(self):
        self.order.delete_order(1)
        self.db.cursor.execute.assert_called_once_with('''DELETE FROM `Order` WHERE order_id = %s''', (1,))
        self.db.conn.commit.assert_called_once()

    def test_list_orders(self):
        self.db.cursor.fetchall.return_value = [(1, 1, 1, 2)]
        result = self.order.list_orders(1)
        self.db.cursor.execute.assert_called_once_with('''SELECT * FROM `Order` WHERE user_id = %s''', (1,))
        self.assertEqual(result, [(1, 1, 1, 2)])

if __name__ == '__main__':
    unittest.main()
