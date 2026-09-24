import sqlite3

#Customer Database
connection = sqlite3.connect("customers.db")
cursor = connection.cursor()



#Creating the customers table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS customers (
        customer_name TEXT PRIMARY KEY,
        plan TEXT,
        purchase_amount FLOAT,
        purchase_item TEXT
    )
    """
)
connection.commit()

#Fake customer data 
customers = [
    ("Globex","Enterprise",300,"SoftwareA"),
    ("Acme", "Pro", 600, "SoftwareB"),
    ("XYZ", "Free", 100, "SoftwareA")
]

#Inserting customer data into Customer table
cursor.executemany(
    """
    INSERT OR IGNORE INTO customers(customer_name,plan,purchase_amount,purchase_item) 
    VALUES(?,?,?,?)
    """, customers
)
connection.commit()

connection2 = sqlite3.connect("tickets.db")
cursor2 = connection2.cursor()

#Creating the tickets table
cursor2.execute(
    """
    CREATE TABLE IF NOT EXISTS tickets(
        ticket_id TEXT PRIMARY KEY,
        customer_name TEXT,
        issue TEXT,
        priority TEXT,
        status TEXT
    )
    """
)
connection2.commit()

#Fake Tickets data
tickets = [
    ("Ticket-101", "Acme", "Export occasionally times out", "medium", "open"),
    ("Ticket-102", "Globex", "Button alignment issue", "low", "open"),
    ("Ticket-103", "XYZ", "Experiencing lag on dashboard page", "high", "closed"),
    ("Ticket-104", "Globex", "Payment page intermittently failing", "high", "open")
]

#Inserting tickets data into Tickets table
cursor2.executemany(
    """
        INSERT OR IGNORE INTO tickets(ticket_id,customer_name,issue, priority,status)
        VALUES(?,?,?,?,?)
    """,tickets
)
connection2.commit()

connection.close()
connection2.close()

