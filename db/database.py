import sqlite3
import hashlib
import json
from datetime import datetime

DATABASE = "orders.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def hash_request_body(body: dict) -> str:
    serialized = json.dumps(body, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def get_idempotency_record(key: str):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM idempotency_records WHERE idempotency_key = ?", (key,)
    ).fetchone()
    conn.close()
    return row


def create_order_atomic(order_id: str, customer_id: str, item_id: str, quantity: int, ledger_id: str,
                        idempotency_key: str, request_hash: str, response_body: dict):

    now = datetime.utcnow().isoformat()
    conn = get_db()
    try:
        conn.execute("BEGIN")

        conn.execute(
            """
            INSERT INTO orders (order_id, customer_id, item_id, quantity, status, created_at)
            VALUES (?, ?, ?, ?, 'created', ?)
            """,
            (order_id, customer_id, item_id, quantity, now)
        )

        conn.execute(
            """
            INSERT INTO ledger (ledger_id, order_id, created_at)
            VALUES (?, ?, ?)
            """,
            (ledger_id, order_id, now)
        )

        conn.execute(
            """
            INSERT INTO idempotency_records (idempotency_key, request_hash, response_body, status_code, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (idempotency_key, request_hash, json.dumps(response_body), 201, now)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_order(order_id: str):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    conn.close()
    return row