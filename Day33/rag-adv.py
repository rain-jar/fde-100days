import uuid
import time
from openai import OpenAI
import logging
import numpy as np
import json

client = OpenAI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chunks = [
    {
        "text": "Refunds for Canadian customers are processed within 5–7 business days.",
        "source": "refunds_canada.txt",
        "country": "CA",
        "department": "support",
        "document_type": "policy",
        "policy_id": "REF-17B"
    },
    {
        "text": "Refunds for US customers are processed within 3–5 business days.",
        "source": "refunds_us.txt",
        "country": "US",
        "department": "support",
        "document_type": "policy",
        "policy_id": "REF-17C"
    },
    {
        "text": "Refunds for UK customers are processed within 7–10 business days.",
        "source": "refunds_uk.txt",
        "country": "UK",
        "department": "support",
        "document_type": "policy",
        "policy_id": "REF-17D"
    },
    {
        "text": "Employees may work internationally for up to 30 days per calendar year.",
        "source": "remote_work_global.txt",
        "country": "GLOBAL",
        "department": "hr",
        "document_type": "policy",
        "policy_id": "REMOTE-22"
    },
    {
        "text": "Canadian employees working remotely must use a company-managed device.",
        "source": "remote_work_canada.txt",
        "country": "CA",
        "department": "hr",
        "document_type": "policy",
        "policy_id": "REMOTE-23"
    },
    {
        "text": "Compromised accounts require an immediate password reset and MFA verification.",
        "source": "security_accounts.txt",
        "country": "GLOBAL",
        "department": "security",
        "document_type": "policy",
        "policy_id": "SEC-91"
    },
    {
        "text": "Enterprise customers receive priority support and a dedicated account manager.",
        "source": "account_plans.txt",
        "country": "GLOBAL",
        "department": "sales",
        "document_type": "plan",
        "policy_id": "PLAN-ENT"
    },
    {
        "text": "Pro customers receive standard support with a four-hour response target.",
        "source": "account_plans.txt",
        "country": "GLOBAL",
        "department": "sales",
        "document_type": "plan",
        "policy_id": "PLAN-PRO"
    },
    {
        "text": "Canadian refund requests above $5,000 require manager approval.",
        "source": "refund_approvals_canada.txt",
        "country": "CA",
        "department": "support",
        "document_type": "procedure",
        "policy_id": "REF-18A"
    },
    {
        "text": "Refund requests involving suspected fraud must be escalated to the security team.",
        "source": "refund_security.txt",
        "country": "GLOBAL",
        "department": "security",
        "document_type": "procedure",
        "policy_id": "SEC-REF-4"
    },
    {
        "text": "Support tickets marked critical require an initial response within 30 minutes.",
        "source": "support_sla.txt",
        "country": "GLOBAL",
        "department": "support",
        "document_type": "policy",
        "policy_id": "SUP-30"
    },
    {
        "text": "UK employees must receive manager approval before international remote work.",
        "source": "remote_work_uk.txt",
        "country": "UK",
        "department": "hr",
        "document_type": "policy",
        "policy_id": "REMOTE-24"
    }
]

with open("current_knowledge_base.json", "r") as file:
    knowledge_base = json.load(file)

#Define cosine similarity for comparing embeddings
def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a) * np.linalg.norm(b))

#Implementing a function for lexical/keyword search
#We need three functions - one to create a searchable text for each chunk, 
# one to score the chunks based on keyword matches, 
# and one to perform the search and return the top results.

#function to create searchable text for each chunk
def create_searchable_text(chunk):
    searchable_text = f"""
    {chunk["text"]}
    {chunk["source"]}
    {chunk["policy_id"]}
    """
    return searchable_text.lower()  # Convert to lowercase for case-insensitive search

#Function to score the chunks
def keyword_score(query, text,chunk):
    #calculate a matching score and return the score
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
        
    overlap = query_words & text_words
    if chunk["policy_id"].lower() in query_words:
        score = 1.0
        return score

    return len(overlap) / max(len(query_words),1)


def keyword_search(query):

    keyword_results = []
    for chunk in knowledge_base:
        keyword_text = create_searchable_text(chunk)
        key_score = keyword_score(query,keyword_text)
        keyword_results.append(
            {
                    "source" : chunk["source"],
                    "text" : chunk["text"],
                    "country" : chunk["country"],
                    "department" : chunk["department"],
                    "document_type" : chunk["document_type"],
                    "policy_id" : chunk["policy_id"],
                    "keyword_score" : key_score,
            }
        )

    keyword_results.sort(key=lambda x:x["keyword_score"], reverse=True)

    return keyword_results

def semantic_score(query_embedding, chunk_embedding):
    min_score = 0.2
    similarity = cosine_similarity(query_embedding, chunk_embedding)
    return similarity

def semantic_search(query_embedding):
    min_score = 0.2
    semantic_results = []
    for chunk in knowledge_base:
        #Apply filters before calculating similarity. For each chunk, check if it matches the filters. If a filter is not specified, it should be ignored.
        # For example, if filters = {"country": "CA", "department": "support"}, then only chunks with country == "CA" and department == "support" should be considered.
        match = True
        for key, value in (filters or {}).items():
            if chunk.get(key) != value:
                match = False
                break
             
        if not match:
            continue

        similarity = cosine_similarity(query_embedding, chunk["embedding"])
        if similarity>=min_score:
            semantic_results.append(
                {
                    "source" : chunk["source"],
                    "text" : chunk["text"],
                    "country" : chunk["country"],
                    "department" : chunk["department"],
                    "document_type" : chunk["document_type"],
                    "policy_id" : chunk["policy_id"],
                    "similarity_score" : similarity
                }
            )

    return semantic_results


def hybrid_search (query, top_k):
    #Create query embedding 
    trace_id = str(uuid.uuid4())[:8]
    embedtimer = time.perf_counter()
    min_semantic_score = 0.2

    #Embed the query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    logger.info(f"{trace_id} : TOP_K is : {top_k}")

    query_embedding = response.data[0].embedding

    hybrid_results =[]
    for chunk in knowledge_base:

        #semantic search
        sem_score = semantic_score(query_embedding, chunk["embedding"])
    
        #keywork search
        keyword_text = create_searchable_text(chunk)
        key_score = keyword_score(query,keyword_text,chunk)

        #hybrid_score
        hybrid_score = (0.7*sem_score + 0.3*key_score)

        if sem_score >= min_semantic_score:
            hybrid_results.append(
                {
                    "source" : chunk["source"],
                    "text" : chunk["text"],
                    "country" : chunk["country"],
                    "department" : chunk["department"],
                    "document_type" : chunk["document_type"],
                    "policy_id" : chunk["policy_id"],
                    "similarity_score" : sem_score,
                    "keyword_score" : key_score,
                    "hybrid_score" : hybrid_score
                }
            )

    hybrid_results.sort(key=lambda x:x["hybrid_score"], reverse=True)

    return hybrid_results[:top_k]







query = "What does REF-17B say about refund processing?"
filters = {
    "country": "ES",
}
results = hybrid_search(query,3)
#results = semantic_search(query,3,0.2,filters=filters)
print(f"Query: {query}")
print(results)