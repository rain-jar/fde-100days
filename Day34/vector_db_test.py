import os
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured") 

conn = psycopg.connect(DATABASE_URL)

register_vector(conn)

print("Connected and pgvector registered successfully.")

conn.close()