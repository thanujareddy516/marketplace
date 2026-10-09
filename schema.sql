-- ============================================
--   SMART VENDOR MARKETPLACE SYSTEM
--   schema.sql - SQLite database schema
--   (Mirrors init_db() in database.py)
-- ============================================

PRAGMA foreign_keys = ON;

-- Vendors who sell on the marketplace
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    license     TEXT    NOT NULL UNIQUE,
    name        TEXT    NOT NULL
                        CHECK(length(name) >= 1),
    status      TEXT    NOT NULL DEFAULT 'Active'
                        CHECK(status IN ('Active', 'Inactive')),
    created_at  TEXT    NOT NULL
);

-- Products listed by vendors
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

-- Customer orders
CREATE TABLE IF NOT EXISTS orders (
    order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    order_code  TEXT    NOT NULL UNIQUE,          -- e.g. ORD-001
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

-- Returns (at most one per order)
CREATE TABLE IF NOT EXISTS returns (
    return_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL UNIQUE
                        REFERENCES orders(order_id)
                        ON DELETE CASCADE,
    reason_code INTEGER NOT NULL CHECK(reason_code IN (1, 2, 3)),
    reason_text TEXT    NOT NULL,                 -- 1 Item damaged, 2 No delivery, 3 Late delivery
    refund_amt  REAL    NOT NULL CHECK(refund_amt >= 0),
    returned_at TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_products_vendor
    ON products(vendor_id);

CREATE INDEX IF NOT EXISTS idx_orders_vendor
    ON orders(vendor_id);

CREATE INDEX IF NOT EXISTS idx_orders_product
    ON orders(product_id);
