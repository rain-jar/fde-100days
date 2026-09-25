import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise RuntimeError("DatabaseURL is not configured")


#Connect to an existing DB
with psycopg.connect(db_url) as conn:

    #Open a cursor to perform DB ops
    with conn.cursor() as cur:

        #Execute a command : SELECT 1
        cur.execute(
            """
                SELECT 1
            """
        )
        print(cur.fetchone())

        # #Create a customers table
        # cur.execute(
        #     """
        #         CREATE TABLE customers (
        #             id SERIAL PRIMARY KEY,
        #             name TEXT UNIQUE NOT NULL,
        #             plan TEXT NOT NULL
        #         );
        #     """
        # )

        #Insert data into the table
        cur.execute(
            """
                INSERT INTO customers(name, plan)
                VALUES(%s,%s)
            """,("Acme","Pro")
        )

        cur.execute(
            """
                INSERT INTO customers(name,plan)
                VALUES(%s,%s)
            """,("Globex","Enterprise")
        )

        #Select all the customer data
        cur.execute("SELECT * FROM customers;")
        print(cur.fetchall())