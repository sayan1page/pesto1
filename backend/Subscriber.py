import redis
import json
import mysql.connector

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Initialize MySQL connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='sayan123',
    database='pesto'
)
cursor = db.cursor()

def process_order(order_data):
    try:
        cursor.execute('''INSERT INTO `Order` (user_id, item_id, item_amount) 
                          VALUES (%s, %s, %s)''', (order_data['user_id'], order_data['item_id'], order_data['item_amount']))
        db.commit()
        print(f"Order processed: {order_data}")
    except Exception as e:
        print(f"Failed to process order: {order_data}, error: {e}")

def main():
    print("Starting Redis subscriber...")
    while True:
        _, order_json = redis_client.blpop('order_queue')
        order_data = json.loads(order_json)
        process_order(order_data)

if __name__ == "__main__":
    main()
