import sqlite3

conn = sqlite3.connect("marketplace.db")
conn.row_factory = sqlite3.Row  # makes rows like dicts

cursor = conn.cursor()

# Change this query to whatever you want
cursor.execute("SELECT * FROM vendors")

rows = cursor.fetchall()
for row in rows:
    print(dict(row))

conn.close()