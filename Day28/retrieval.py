from openai import OpenAI
import os
import json
import numpy as np

client = OpenAI()

#RETRIEVAL PIPELINE

with open("knowledge_base.json", "r") as file:
    knowledge_base = json.load(file)

#Define cosine similarity for comparing embeddings
def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a) * np.linalg.norm(b))

def semantic_search(query, top_k, min_score):
    #Create query embedding 
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    #Embed the query
    query_embedding = response.data[0].embedding

    results = []
    for knowledge in knowledge_base:
        #calculate similarity
        similarity = cosine_similarity(query_embedding,knowledge["embedding"])
        if similarity>=min_score:
            results.append(
                {
                    "source" : knowledge["source"],
                    "text" : knowledge["text"],
                    "score" : similarity
                }
            )

        results.sort(key=lambda x:x["score"], reverse=True)

    return results[:top_k]

# results = semantic_search("What is the Enterprise refund policy?",3,0.2)
# for result in results:
#     print(result["source"], result["score"])
#     print(result["text"])
#     print()

def answer_query(user_question):
    #Do a semantic search
    results = semantic_search(user_question,3,0.2)

    #Structure the search results for an LLM
    llm_input = []
    for result in results:
        llm_input.append(f"""
            SOURCE : {result["source"]}
            CONTENT : {result["text"]}
            """
        )

    #Pass the structured input to an LLM
    response = client.responses.create(
        model="gpt-5.6",
        input = [
            {
                "role" : "system",
                "content":"Answer only using the provided context data. Also, for any factual claim include its source filename in square brackets. And if the source doesn't support the answer, say so and abstain from answering. And while abstaining, no need to cite anything"
            },
            {
                "role": "user",
                "content": f"""
                    QUESTION : {user_question}
                    CONTEXT : {llm_input}
                    """
            }
        ]
    )

    # print("RETRIEVED:")
    # for result in results:
    #     print(result["source"], result["score"], "-" ,result["text"])

    # print("\n ANSWER:")
    # print(response.output_text)


#answer_query("What's our refund policy for Enterprise customers?")