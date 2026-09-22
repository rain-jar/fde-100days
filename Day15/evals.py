from openai import OpenAI
import os
import json
import numpy as np

eval_cases = [
    {
        "question" : "Can Enterprise customers who use promotion cards get a refund. And how long does it take?",
        "expected_source" : "refunds.txt",
        "expected_fact" : "No. Refunds are not available for promotional credits"
    },
    {
        "question" : "Can Acme's remote employees access internal systems",
        "expected_source" : "remote_work.txt",
        "expected_fact" : "Yes. Employees working remotely must use an Acme-managed device when accessing internal systems"
    },
    {
        "question" : "How long is international remote work permitted",
        "expected_source" : "remote_work.txt",
        "expected_fact" : "International remote work is generally permitted for a maximum of 30 calendar days during any rolling 12-month period"
    },
    {
        "question" : "Can a remote Acme employee access customer information, and what device must they use?",
        "expected_source" : ["remote_work.txt","security.txt"],
        "expected_fact" : "Yes. Employees may access customer information only when required for their job responsibilities. But employees working remotely must use an Acme-managed device when accessing internal systems"
    },
    {
        "question" : "How long is Acme's maternity leave duration",
        "should_abstain" : True
    }
    
]

client = OpenAI()

###RETRIEVAL PIPELINE
#Read the json embeddings data
with open("knowledge_base.json","r") as file:
    knowledge_base = json.load(file)
#print(len(knowledge_base))

#Define cosine similarity for comparing embeddings
def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a) * np.linalg.norm(b))

#Function to do a semantic search for a user_query and return results
def semantic_search(query,top_k,min_score):
    #Create embedding for the query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding

    results = []
    for knowledge in knowledge_base:
        similarity = cosine_similarity(query_embedding, knowledge["embedding"])
        if similarity >= min_score:
            results.append(
                {
                    "source" : knowledge["source"],
                    "text" : knowledge["text"],
                    "score" : similarity
                }
            )

    results.sort(key=lambda x:x["score"], reverse=True)
    return results[:top_k]

#Funtion to answer a question -
# by providing the results of the search to an LLM as context
def answer_query(query):
    #Do a semantic search
    results = semantic_search(query, top_k=5, min_score=0.2)

    #Structure the search results for an LLM
    llm_input = []
    for result in results:
        llm_input.append(f"""
            SOURCE : {result["source"]}
            CONTENT : {result["text"]}
            """
        )

    #Pass the structured context to the LLM
    response = client.responses.create(
        model="gpt-5.6",
        input= [
            {
                "role" : "system",
                "content" : "Answer only using the provided context data. Also, for any factual claim include its source filename in square brackets. And if the source doesn't support the answer, say so and abstain from answering. And while abstaining, no need to cite anything"
            },
            {
                "role" : "user",
                "content" : f"""
                        QUESTION : {query}
                        CONTEXT : {llm_input}
                        """
            }
        ]
    )

    # print("RETRIEVED:")
    # for result in results:
    #      print(result["source"], result["score"], "-" ,result["text"])

    # print("\n ANSWER:")
    # print(response.output_text)
    return response

#Reading Evals from a Dataset Json file
with open("eval_dataset.json","r") as file:
    eval_dataset = json.load(file)

print(len(eval_dataset))

resultbase = []
for eval in eval_dataset:
    result = answer_query(eval["question"])
    resultbase.append(
        {
            "id" : eval["id"],
            "category" : eval["category"],
            "answer" : result.output_text,
            "source" : eval["expected_sources"],
            "expected_answer" : eval["expected_answer"],
            "should_abstain" : eval["should_abstain"]
        }
    )

print(len(resultbase))

for result in resultbase:
    print("\n Eval : ", result)