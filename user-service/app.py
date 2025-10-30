from flask import Flask, request, jsonify
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")

def get_conn():
    # Retry logic because DB may not be ready immediately
    max_retries = 8
    delay = 2
    last_err = None
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            last_err = e
            time.sleep(delay)
    raise last_err

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    if not data or "name" not in data or "email" not in data:
        return jsonify({"message": "name and email required"}), 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email",
                (data["name"], data["email"])
            )
            user = cur.fetchone()
    return jsonify(user), 201

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users WHERE id=%s", (user_id,))
            user = cur.fetchone()
            if not user:
                return jsonify({"message": "not found"}), 404
    return jsonify(user)

if __name__ == "__main__":
    # listen on 0.0.0.0 for container
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))