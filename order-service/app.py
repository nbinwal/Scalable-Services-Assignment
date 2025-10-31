from flask import Flask, request, jsonify
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")

def get_conn():
    retries = 8
    for _ in range(retries):
        try:
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        except Exception:
            time.sleep(2)
    raise RuntimeError("Could not connect to DB")

def ensure_orders_table():
    sql = """
    CREATE TABLE IF NOT EXISTS orders (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL,
      book_id VARCHAR(50) NOT NULL,
      qty INTEGER NOT NULL DEFAULT 1,
      status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
      created_at TIMESTAMP DEFAULT current_timestamp
    );
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    book_id = data.get('book_id')
    qty = data.get('qty', 1)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO orders (user_id, book_id, qty) VALUES (%s,%s,%s) RETURNING id,user_id,book_id,qty,status,created_at",
                        (user_id, book_id, qty))
            order = cur.fetchone()
    return jsonify(order), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,user_id,book_id,qty,status,created_at FROM orders WHERE id=%s", (order_id,))
            order = cur.fetchone()
            if not order:
                return jsonify({'message':'not found'}), 404
    return jsonify(order)

if __name__ == '__main__':
    ensure_orders_table()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5002)))