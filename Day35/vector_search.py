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

def hybrid_search(query: str, top_k:int=3, country: str| None=None):

    results = semantic_search(query, top_k=10, country=country)
    for result in results:
        #check if the policy id for this result is mentioned in the query
        if result["policy_id"] and result["policy_id"].lower() in query.lower():
            result["keyword_score"] = 1.0
        else:
            result["keyword_score"] = 0.0

        result["hybrid_score"] = 0.7 * result["similarity"] + 0.3 * result["keyword_score"]

    sorted_results = sorted(results, key=lambda x: x["hybrid_score"], reverse=True)
    return sorted_results[:top_k]


#results = semantic_search("What does REF-17B say about refund processing?", top_k=5)
results = hybrid_search("What is the parental leave policy for Northstar?", top_k=5)
for row in results:
    print(row)
