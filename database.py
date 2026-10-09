"""
database.py - SQLite data layer for Smart Vendor Marketplace System.

Stores structured records in himage.db (vendors, products, orders, returns).
Image bytes stay in the filesystem; here, order and product data are stored
as rows so metadata can be queried, joined, and reported on.

Every public function here uses parameterized SQL to avoid SQL injection.
SQLite connection context managers commit on success and roll back on error.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "marketplace.db"


# ---------------------------------------------------------------------------
# Schema setup
# ---------------------------------------------------------------------------

def init_db(db_path: str = DB_PATH) -> None:
    """Create all tables if they do not already exist."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS vendors (
                vendor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                license     TEXT    NOT NULL UNIQUE,
                name        TEXT    NOT NULL
                                    CHECK(length(name) >= 1),
                status      TEXT    NOT NULL DEFAULT 'Active'
                                    CHECK(status IN ('Active', 'Inactive')),
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                product_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id   INTEGER NOT NULL
                                    REFERENCES vendors(vendor_id)
                                    ON DELETE CASCADE,
                name        TEXT    NOT NULL,
                orig_price  REAL    NOT NULL CHECK(orig_price > 0),
                sell_price  REAL    NOT NULL CHECK(sell_price > orig_price),
                stock       INTEGER NOT NULL CHECK(stock >= 0),
                added_at    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                order_code  TEXT    NOT NULL UNIQUE,
                vendor_id   INTEGER NOT NULL
                                    REFERENCES vendors(vendor_id),
                product_id  INTEGER NOT NULL
                                    REFERENCES products(product_id),
                quantity    INTEGER NOT NULL CHECK(quantity > 0),
                subtotal    REAL    NOT NULL CHECK(subtotal >= 0),
                handling    REAL    NOT NULL CHECK(handling >= 0),
                delivery    REAL    NOT NULL CHECK(delivery >= 0),
                total       REAL    NOT NULL CHECK(total >= 0),
                profit      REAL    NOT NULL,
                status      TEXT    NOT NULL DEFAULT 'Delivered'
                                    CHECK(status IN ('Delivered', 'Returned')),
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS returns (
                return_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id    INTEGER NOT NULL UNIQUE
                                    REFERENCES orders(order_id)
                                    ON DELETE CASCADE,
                reason_code INTEGER NOT NULL CHECK(reason_code IN (1, 2, 3)),
                reason_text TEXT    NOT NULL,
                refund_amt  REAL    NOT NULL CHECK(refund_amt >= 0),
                returned_at TEXT    NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_products_vendor
                ON products(vendor_id);

            CREATE INDEX IF NOT EXISTS idx_orders_vendor
                ON orders(vendor_id);

            CREATE INDEX IF NOT EXISTS idx_orders_product
                ON orders(product_id);
        """)


# ---------------------------------------------------------------------------
# Vendor operations
# ---------------------------------------------------------------------------

def add_vendor(license: str, name: str, db_path: str = DB_PATH) -> int:
    """
    Insert a new vendor and return its vendor_id.
    Raises sqlite3.IntegrityError if the license already exists.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            "INSERT INTO vendors (license, name, created_at) VALUES (?, ?, ?)",
            (license, name, datetime.now().isoformat())
        )
        return cur.lastrowid


def get_vendor(license: str, db_path: str = DB_PATH) -> dict | None:
    """Return the vendor row as a dict, or None if not found."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM vendors WHERE license = ?", (license,)
        ).fetchone()
        return dict(row) if row else None


def list_vendors(db_path: str = DB_PATH) -> list[dict]:
    """Return all vendors ordered by name."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM vendors ORDER BY name"
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Product operations
# ---------------------------------------------------------------------------

def add_product(vendor_id: int, name: str, orig: float,
                sell: float, stock: int, db_path: str = DB_PATH) -> int:
    """Insert a product and return its product_id."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            """INSERT INTO products
               (vendor_id, name, orig_price, sell_price, stock, added_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (vendor_id, name, orig, sell, stock, datetime.now().isoformat())
        )
        return cur.lastrowid


def get_product(name: str, db_path: str = DB_PATH) -> dict | None:
    """Return a product row by name, or None."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM products WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else None


def update_stock(product_id: int, new_stock: int, db_path: str = DB_PATH) -> None:
    """Update the stock for a product."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "UPDATE products SET stock = ? WHERE product_id = ?",
            (new_stock, product_id)
        )


def list_products(db_path: str = DB_PATH) -> list[dict]:
    """Return all products with vendor name, ordered by name."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT p.product_id, p.name, p.orig_price, p.sell_price, p.stock,
                   v.name AS vendor_name, v.license
            FROM products AS p
            JOIN vendors  AS v ON v.vendor_id = p.vendor_id
            ORDER BY p.name
        """).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Order operations
# ---------------------------------------------------------------------------

def save_order(order_code: str, vendor_id: int, product_id: int,
               qty: int, subtotal: float, handling: float,
               delivery: float, total: float, profit: float,
               db_path: str = DB_PATH) -> int:
    """Insert a new order and return its order_id."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            """INSERT INTO orders
               (order_code, vendor_id, product_id, quantity,
                subtotal, handling, delivery, total, profit, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_code, vendor_id, product_id, qty,
             subtotal, handling, delivery, total, profit,
             datetime.now().isoformat())
        )
        return cur.lastrowid


def next_order_number(db_path: str = DB_PATH) -> int:
    """Return the next free order number (e.g. 4 if 'ORD-003' is the highest)."""
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT MAX(CAST(SUBSTR(order_code, 5) AS INTEGER)) FROM orders"
        ).fetchone()
        return (row[0] or 0) + 1


def get_order_by_code(order_code: str, db_path: str = DB_PATH) -> dict | None:
    """Return an order row by its display code (e.g. 'ORD-001'), or None."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM orders WHERE order_code = ?", (order_code,)
        ).fetchone()
        return dict(row) if row else None


def mark_order_returned(order_id: int, db_path: str = DB_PATH) -> None:
    """Set an order's status to 'Returned'."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "UPDATE orders SET status = 'Returned' WHERE order_id = ?",
            (order_id,)
        )


def list_all_orders(db_path: str = DB_PATH) -> list[dict]:
    """Return every order with product name and vendor license."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT o.*, p.name AS product_name, v.license
            FROM orders   AS o
            JOIN products AS p ON p.product_id = o.product_id
            JOIN vendors  AS v ON v.vendor_id  = o.vendor_id
            ORDER BY o.order_id
        """).fetchall()
        return [dict(r) for r in rows]


def list_orders_for_vendor(vendor_id: int, db_path: str = DB_PATH) -> list[dict]:
    """Return all orders for a vendor with product name."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT o.order_code, p.name AS product_name,
                   o.quantity, o.total, o.status, o.created_at
            FROM orders   AS o
            JOIN products AS p ON p.product_id = o.product_id
            WHERE o.vendor_id = ?
            ORDER BY o.order_id
        """, (vendor_id,)).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Return operations
# ---------------------------------------------------------------------------

REASON_TEXT = {
    1: "Item damaged",
    2: "No delivery",
    3: "Late delivery"
}


def save_return(order_id: int, reason_code: int,
                refund_amt: float, db_path: str = DB_PATH) -> int:
    """Insert a return record and return its return_id."""
    reason_text = REASON_TEXT.get(reason_code, "Unknown")
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            """INSERT INTO returns
               (order_id, reason_code, reason_text, refund_amt, returned_at)
               VALUES (?, ?, ?, ?, ?)""",
            (order_id, reason_code, reason_text,
             refund_amt, datetime.now().isoformat())
        )
        return cur.lastrowid


# ---------------------------------------------------------------------------
# Report queries
# ---------------------------------------------------------------------------

def report_summary(db_path: str = DB_PATH) -> dict:
    """
    Return aggregated report data:
    - total_revenue: SUM of all order totals
    - handling_total, delivery_total: SUM across all orders
    - net_app_profit: handling + delivery - SUM(refund_amt from returns)
    - vendor_profit: SUM of profit from Delivered orders only
    """
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("""
            SELECT
                COALESCE(SUM(total),    0) AS total_revenue,
                COALESCE(SUM(handling), 0) AS handling_total,
                COALESCE(SUM(delivery), 0) AS delivery_total,
                COALESCE(SUM(CASE WHEN status = 'Delivered' THEN profit ELSE 0 END), 0)
                    AS vendor_profit
            FROM orders
        """).fetchone()

        refund_row = conn.execute(
            "SELECT COALESCE(SUM(refund_amt), 0) FROM returns"
        ).fetchone()

        refund = refund_row[0]
        return {
            "total_revenue" : round(row[0], 2),
            "handling_total": round(row[1], 2),
            "delivery_total": round(row[2], 2),
            "net_app_profit": round(row[1] + row[2] - refund, 2),
            "vendor_profit" : round(row[3], 2),
        }


def count_images_per_vendor(db_path: str = DB_PATH) -> list[dict]:
    """Count products listed by each vendor (LEFT JOIN + GROUP BY demo)."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT v.name AS vendor_name,
                   COUNT(p.product_id) AS product_count
            FROM vendors  AS v
            LEFT JOIN products AS p ON p.vendor_id = v.vendor_id
            GROUP BY v.vendor_id, v.name
            ORDER BY product_count DESC
        """).fetchall()
        return [dict(r) for r in rows]


def order_history_for_product(product_name: str, db_path: str = DB_PATH) -> list[dict]:
    """Return all orders ever placed for a named product."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT o.order_code, o.quantity, o.total, o.status, o.created_at
            FROM orders   AS o
            JOIN products AS p ON p.product_id = o.product_id
            WHERE p.name = ?
            ORDER BY o.order_id
        """, (product_name,)).fetchall()
        return [dict(r) for r in rows]
        