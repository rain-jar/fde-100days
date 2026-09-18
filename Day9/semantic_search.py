from openai import OpenAI
import numpy as np

client = OpenAI()

#List of all the tickets for customer
tickets = [
    "Customers cannot complete checkout because the payment button freezes.",
    "Exporting reports to CSV occasionally times out.",
    "Users are being charged twice for the same purchase.",
    "The dashboard takes over 20 seconds to load.",
    "Customers cannot reset their passwords.",
    "Credit cards are being declined unexpectedly.",
    "Profile pictures sometimes fail to upload.",
    "Invoices display the wrong company address",
    "The office coffee machine has stopped working"
]

#Create embedding for all the tickets
ticket_embeddings = []
for ticket in tickets:
    #create embedding
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=ticket
    )
    embedding = response.data[0].embedding

    #Add the strings and their respective embeddings to a dictionary
    ticket_embeddings.append(
        {
            "text" : ticket,
            "embedding" : embedding
        }
    )

#Define a cosine similarity function
def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a) * np.linalg.norm(b))

#Function that does semantic searh : 
# takes the user query, 
# creates an embedding for that query,
# calculates the similarity score for that query against every ticket
# returns the tickets with the top 3 (or k) similarity scores. 

def semantic_search(query,top_k):
    #user_query = input("You: ")
    query_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = query_response.data[0].embedding

    results = []

    for ticket in ticket_embeddings:
        similarity = cosine_similarity(ticket["embedding"], query_embedding)
        results.append(
            {
                "text" : ticket["text"],
                "score" : similarity
            }
        )

    results.sort(key=lambda x:x["score"], reverse=True)
    return results[:top_k]


#Test run of a semantic search
results = semantic_search(
    "Are there account access problems",
    top_k = 3
)

print(results)