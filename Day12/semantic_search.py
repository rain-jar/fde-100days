from openai import OpenAI
import numpy as np

client = OpenAI()

#List of all the tickets for customer
tickets = [
    {
        "id" : "Ticket-101",
        "text" : "Password reset emails aren't arriving."
    },
    {
        "id" : "Ticket-102",
        "text" : "Users cannot reset passwords after clicking the reset link."
    },
    {
        "id" : "Ticket-103",
        "text" : "Password reset emails sometimes arrive 20 minutes late."
    },
    {
        "id" : "Ticket-104",
        "text" : "Users cannot log in after changing their password."
    },
    {
        "id" : "Ticket-105",
        "text" : "Users cannot log in after changing their email address."
    },
    {
        "id" : "Ticket-106",
        "text" : "Login attempts fail even with the correct password."
    },
    {
        "id" : "Ticket-107",
        "text" : "Email notifications sometimes arrive late."
    },
    {
       "id" : "Ticket-108",
        "text" : "Users aren't receiving account notification emails."
    },
    {
        "id" : "Ticket-109",
        "text" : "Customers are being charged twice for the same purchase."
    },
    {
        "id" : "Ticket-110",
        "text" : "Credit card payments are being declined."
    },
    {
        "id" : "Ticket-111",
        "text" : "Customers cannot update their billing information."
    },
    {
        "id" : "Ticket-112",
        "text" : "Invoices show the wrong billing amount."
    },
    {
        "id" : "Ticket-113",
        "text" :  "CSV exports fail to download."
    },
    {
        "id" : "Ticket-114",
        "text" : "Large exports take several minutes to complete."
    },
    {
        "id" : "Ticket-115",
        "text" : "The analytics dashboard loads very slowly."
    },
    {
        "id" : "Ticket-116",
        "text" : "The dashboard sometimes displays outdated data."
    },
    {
        "id" : "Ticket-117",
        "text" : "Users cannot update their profile picture."
    },
    {
        "id" : "Ticket-118",
        "text" : "Profile changes are not being saved."
    },
    {
        "id" : "Ticket-119",
        "text" : "Payment confirmation emails aren't being received."
    },
    {
        "id" : "Ticket-120",
        "text" : "Users receive password reset emails but the links have expired."
    }
]

support_document = """
PAYMENTS
Customers may occasionally experience failed or declined card payments.
Duplicate charges can occur when a payment request is submitted multiple
times. Customers should verify their transaction history before retrying
a failed payment. Billing information can be updated from account settings.

PASSWORD RESET
Customers who forget their password can request a password reset email.
Some customers report that password reset emails do not arrive or are
significantly delayed. Customers should check their spam folder before
requesting another email. Reset links expire after a limited period and
customers must request a new email if the link has expired.

EXPORTS
Customers can export account data as CSV files from the dashboard.
Large exports may take several minutes to generate. Occasionally an export
may fail before the download begins. Customers should retry the export
or reduce the amount of data included in the request.

NOTIFICATIONS
The application sends email notifications for important account activity.
Some notifications may be delayed because of email delivery issues.
Customers can configure which notifications they receive from their
profile settings. Notification preferences do not affect password reset
emails.
"""

chunks = [
    """PAYMENTS
    Customers may occasionally experience failed or declined card payments.
    Duplicate charges can occur when a payment request is submitted multiple
    times. Customers should verify their transaction history before retrying
    a failed payment. Billing information can be updated from account settings.""",

    """PASSWORD RESET
    Customers who forget their password can request a password reset email.
    Some customers report that password reset emails do not arrive or are
    significantly delayed. Customers should check their spam folder before
    requesting another email. Reset links expire after a limited period and
    customers must request a new email if the link has expired.""",

    """EXPORTS
    Customers can export account data as CSV files from the dashboard.
    Large exports may take several minutes to generate. Occasionally an export
    may fail before the download begins. Customers should retry the export
    or reduce the amount of data included in the request.""",

    """NOTIFICATIONS
    The application sends email notifications for important account activity.
    Some notifications may be delayed because of email delivery issues.
    Customers can configure which notifications they receive from their
    profile settings. Notification preferences do not affect password reset
    emails."""
]


#Create embedding for all the tickets
ticket_embeddings = []
for ticket in tickets:
    #create embedding
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=ticket["text"]
    )
    embedding = response.data[0].embedding

    #Add the strings and their respective embeddings to a dictionary
    ticket_embeddings.append(
        {
            "id" : ticket["id"],
            "text" : ticket["text"],
            "embedding" : embedding
        }
    )
print(len(ticket_embeddings))

#Define a cosine similarity function
def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a) * np.linalg.norm(b))

query = "Why aren't password reset emails arriving?"
query_response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)
query_embedding = query_response.data[0].embedding

#chunk_embeddings = []
# for chunk in chunks:
#     #embed the chunk
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=chunk
#     )
#     chunk_embedding = response.data[0].embedding
#     #find similarity for each against the query
#     chunk_similarity = cosine_similarity(chunk_embedding, query_embedding)
#     #print it
#     print(chunk_similarity,chunk)



#Function that does semantic searh for a given question : 
# takes the user query, 
# creates an embedding for that query,
# calculates the similarity score for that query against every ticket
# returns the tickets with the top 3 (or k) similarity scores. 

def semantic_search(query,top_k, min_score):
    #user_query = input("You: ")
    query_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = query_response.data[0].embedding

    results = []

    for ticket in ticket_embeddings:
        similarity = cosine_similarity(ticket["embedding"], query_embedding)
        if similarity >= min_score:
            results.append(
                {
                    "id" : ticket["id"],
                    "text" : ticket["text"],
                    "score" : similarity
                }
            )

    results.sort(key=lambda x:x["score"], reverse=True)
    return results[:top_k]

#Function that :
# calls semantic search, 
# collects the results, 
# gives to the LLM and 
# retrieves the answer to a question
def answer_question(question):
    #does the semantic search
    results = semantic_search(question, top_k=3, min_score=0.2)

    #collect the search to create the context
    support_tickets = []
    for result in results:
        support_tickets.append(f"""
            SOURCE : {result["id"]}
            CONTENT : {result["text"]}
            """
        )

    #consolidate into a LLM input string
    context = "\n".join(support_tickets)

    #call the LLM and pass the question and the context
    response = client.responses.create(
        model="gpt-5.6",
        input= [
            {"role" : "system","content":"Answer only using the supplied support-ticket context. Also, for any factual claim include its source ID in square brackets. And if the source doesn't support the answer, say so and abstain from answering. And while abstaining, no need to cite anything "},
            {
                "role" : "user",
                "content": f"""
                QUESTION {question}
                CONTEXT {context}
                """
            }
        ]
    )
    print("RETRIEVED:")
    for result in results:
        print(result["id"], "-" ,result["text"])

    print("\n ANSWER:")
    print(response.output_text)

answer_question("What problems are customers having with the iOS app?")
