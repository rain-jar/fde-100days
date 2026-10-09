from dotenv import load_dotenv
import os
from openai import OpenAI
import psycopg
from pgvector.psycopg import register_vector
from pgvector import Vector
import time
import random

from trio import current_time


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


#Implement Caching for the vector search results
retrieval_cache = {}
CACHE_TTL = 5 #Cache time-to-live in seconds (5 minutes)

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

def search_with_cache(query: str, top_k:int=3, country: str| None=None):
    cache_key = (query, top_k, country) #create a unique cache key based on the query, top_k, and country

    #Check if the cache key exists
    if cache_key in retrieval_cache:
        age = time.time() - retrieval_cache[cache_key]["created_at"] #calculate the age of the cached result
        if age < CACHE_TTL: #check if the cached result is still valid
            print("Cache hit for query:", query)
            return retrieval_cache[cache_key]["results"] #return the cached result
        else:
            print("Cache expired for query:", query)
            del retrieval_cache[cache_key] #delete the expired cache entry
            
    print("Cache miss for query:", query)
    results = hybrid_search(query, top_k=top_k, country=country) #do the search

    retrieval_cache[cache_key] = {#store the results in the cache and set the timestamp
        "results": results,
        "created_at": time.time()
    }
    return results

#Building rate limits per user
request_history = {}
rate_limit = 5 #max requests per minute
rate_window = 10 #time window in seconds

def check_rate_limit(user_id: str):
    current_time = time.time()

    timestamps = request_history.get(user_id, [])
    
    #Remove requests that are outside the rate window
    timestamps = [
        timestamp 
        for timestamp in timestamps 
        if current_time - timestamp < rate_window
    ]

    if len(timestamps) >= rate_limit:
        request_history[user_id] = timestamps #Update the request history for the user
        return False #Rate limit exceeded

    #record this request
    timestamps.append(current_time)
    request_history[user_id] = timestamps #Update the request history for the user
    return True #Request allowed

#Test the rate limiting function
# for i in range(7):
#     allowed = check_rate_limit("USER-101")

#     if allowed:
#         print(f"Request {i+1} 200 OK for USER-101")   
#     else:
#         print(f"Request {i+1} 429 Too Many Requests for USER-101")                     

# time.sleep(11) #wait for 11 seconds to reset the rate limit window
# allowed = check_rate_limit("USER-101")
# if allowed:
#     print("Request 8 200 OK for USER-101")
# else:
#     print("Request 8 429 Too Many Requests for USER-101")


#Building Resilience with Backoff and Jitter
attempt_count = 0
def unreliable_dependency():
    global attempt_count
    attempt_count += 1
    if attempt_count < 1000:
        raise ConnectionError("503 Service Unavailable")
    
    return "Success"

def call_with_retry(max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            result = unreliable_dependency()
            print(f"Attempt {attempt + 1} succeeded: {result}")
            return result
        except ConnectionError as error:
            print(f"Attempt {attempt + 1} failed: {error}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1) #Exponential backoff with jitter
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Giving up.")
                raise

result = call_with_retry()

# start = time.perf_counter()

# results = search_with_cache("What is the Canadian refund policy?", top_k=5, country="CA")

# elapsed = time.perf_counter() - start
# print(f"Latency for first search: {elapsed:.4f} seconds")
# # for row in results:
# #     print(row)


# start = time.perf_counter()
# results = search_with_cache("What is the Canadian refund policy?", top_k=5, country="CA")
# elapsed = time.perf_counter() - start
# print(f"Latency for second search: {elapsed:.4f} seconds")

# #wait for 6 seconds to let the cache expire
# time.sleep(6)

# start = time.perf_counter()
# results = search_with_cache("What is the Canadian refund policy?", top_k=5, country="CA")
# elapsed = time.perf_counter() - start
# print(f"Latency for third search: {elapsed:.4f} seconds")

# # for row in results:
# #     print(row)




