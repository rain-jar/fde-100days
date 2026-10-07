import os
import psycopg 
import json
from dotenv import load_dotenv
from openai import OpenAI
from pgvector.psycopg import register_vector

load_dotenv()
client = OpenAI()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

with open("current_knowledge_base.json", "r") as file:
    knowledge_base = json.load(file)

#Connect to PostgreSQL and insert the chunk with its embedding
with psycopg.connect(DATABASE_URL) as conn:
    register_vector(conn)

    with conn.cursor() as cur:
        for chunk in knowledge_base:
            cur.execute(
                """
                INSERT INTO knowledge_chunks (content, source, country, department, document_type, policy_id, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    chunk["text"],
                    chunk["source"],
                    chunk["country"],
                    chunk["department"],
                    chunk["document_type"],
                    chunk["policy_id"],
                    chunk["embedding"]
                )
            )

print(f"Inserted {len(knowledge_base)} chunks into the knowledge_chunks table.")
