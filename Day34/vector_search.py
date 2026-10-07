from dotenv import load_dotenv
import os
from openai import OpenAI
import psycopg
from pgvector.psycopg import register_vector
from pgvector import Vector

load_dotenv()
client = OpenAI()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

def semantic_search(query: str, top_k:int=3, country: str | None=None):
    #Embed the query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = Vector(response.data[0].embedding)

    #Let Postgres handle the vector search
    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)

        with conn.cursor() as cur:
            if country:
                cur.execute(
                    """
                        SELECT
                            content,
                            source,
                            country,
                            policy_id,
                            1 - (embedding <=> %s) AS similarity
                        FROM knowledge_chunks
                        WHERE country = %s
                        ORDER BY embedding <=> %s
                        LIMIT %s;
                    """,
                    (query_embedding, country, query_embedding, top_k)
                )
            else:
                cur.execute(
                    """
                        SELECT
                            content,
                            source,
                            country,
                            policy_id,
                            1 - (embedding <=> %s) AS similarity
                        FROM knowledge_chunks
                        ORDER BY embedding <=> %s
                        LIMIT %s;
                    """,
                    (query_embedding, query_embedding, top_k)
                )

            rows = cur.fetchall()

    return [
        {
            "content": row[0],
            "source": row[1],
            "country": row[2],
            "policy_id": row[3],
            "similarity": row[4]
        } 
        for row in rows
    ]

results = semantic_search("How long do refunds take?", top_k=3)

for row in results:
    print(row)
