import sqlite3

connection = sqlite3.connect("customers.db")
cursor = connection.cursor()

cursor.execute(
    """
        ALTER TABLE customers
        ADD COLUMN purchase_date TEXT
    """
)

cursor.execute(
    """
        UPDATE customers
        SET purchase_date = ?
        WHERE customer_name = ?
    """,("2026-09-01","Globex")
)
connection.commit()