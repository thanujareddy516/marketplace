# Smart Vendor Marketplace System

A command-line marketplace where vendors register, list products, take orders, and process returns. All data is stored in a local SQLite database (`marketplace.db`).

## Features

- **Vendor login / register** using a numeric license number
- **Add products** with original price, selling price, and stock
- **View products** from all vendors
- **Place orders** with automatic billing and stock updates
- **Return orders** with a reason (item damaged, no delivery, late delivery)
- **Merchant report** showing revenue, fees, refunds, and profit

## Billing rules

| Item | Rule |
|---|---|
| Handling fee | 10% of subtotal |
| Delivery charge | Rs.50, free when subtotal is Rs.500 or more |
| Vendor profit | (selling price − original price) × quantity |
| Order ID | `ORD-001`, `ORD-002`, … |

## Project structure

```
marketplace/
├── main.py              # CLI menu and user interaction
├── logic.py             # Pure functions: validation, billing, reports
├── database.py          # SQLite data layer (parameterized queries)
├── query.py             # Helper script to run ad-hoc SQL queries
├── test.py              # Unit tests for logic.py
├── schema.sql           # Database schema (tables and indexes)
├── requirements.txt     # Python dependencies
└── .github/workflows/
    └── ci.yml           # GitHub Actions: runs tests on push / PR
```

## Database schema

Four tables, defined in [schema.sql](schema.sql) and created automatically by `init_db()` on startup:

- `vendors`: license, name, status
- `products`: belongs to a vendor; selling price must be greater than original price
- `orders`: belongs to a vendor and product; status is `Delivered` or `Returned`
- `returns`: one per order, with reason code and refund amount

## Setup

Requires Python 3.10 or newer. The app itself uses only the standard library; `pytest` is needed for tests.

```bash
pip install -r requirements.txt
```

## Usage

Run the app from inside the `marketplace` folder:

```bash
python main.py
```

```
--- MAIN MENU ---
1. Vendor Login / Register
2. Add Product
3. View Products
4. Place Order
5. Return Order
6. Merchant Report
7. Exit
```

Log in (option 1) before adding products or placing orders.

To inspect the database, edit the SQL in `query.py` and run:

```bash
python query.py
```

You can also create an empty database straight from the schema:

```bash
sqlite3 marketplace.db < schema.sql
```

## Running tests

```bash
pytest test.py -v
```

## Continuous integration

`.github/workflows/ci.yml` runs on every push to `main` and on pull requests. It installs dependencies, checks that `schema.sql` loads, and runs the test suite on Python 3.10, 3.12, and 3.13.
