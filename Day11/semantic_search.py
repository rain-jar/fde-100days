from openai import OpenAI
import numpy as np

client = OpenAI()

#List of all the tickets for customer
tickets = [
    "Password reset emails aren't arriving.",
    "Users cannot reset passwords after clicking the reset link.",
    "Password reset emails sometimes arrive 20 minutes late.",
    "Users cannot log in after changing their password.",
    "Users cannot log in after changing their email address.",
    "Login attempts fail even with the correct password.",
    "Email notifications sometimes arrive late.",
    "Users aren't receiving account notification emails.",
    "Customers are being charged twice for the same purchase.",
    "Credit card payments are being declined.",
    "Customers cannot update their billing information.",
    "Invoices show the wrong billing amount.",
    "CSV exports fail to download.",
    "Large exports take several minutes to complete.",
    "The analytics dashboard loads very slowly.",
    "The dashboard sometimes displays outdated data.",
    "Users cannot update their profile picture.",
    "Profile changes are not being saved.",
    "Payment confirmation emails aren't being received.",
    "Users receive password reset emails but the links have expired."
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
# for ticket in tickets:
#     #create embedding
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=ticket
#     )
#     embedding = response.data[0].embedding

#     #Add the strings and their respective embeddings to a dictionary
#     ticket_embeddings.append(
#         {
#             "text" : ticket,
#             "embedding" : embedding
#         }
#     )
# print(len(ticket_embeddings))

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
for chunk in chunks:
    #embed the chunk
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk
    )
    chunk_embedding = response.data[0].embedding
    #find similarity for each against the query
    chunk_similarity = cosine_similarity(chunk_embedding, query_embedding)
    #print it
    print(chunk_similarity,chunk)



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
    results = semantic_search(question, top_k=3)

    #collect the search to create the context
    support_tickets = []
    for result in results:
        support_tickets.append(result["text"])

    #consolidate into a LLM input string
    context = "\n".join(support_tickets)

    #call the LLM and pass the question and the context
    response = client.responses.create(
        model="gpt-5.6",
        input= [
            {"role" : "system","content":"Answer only using the supplied support-ticket context. If the context does not contain enough information to answer the question, say so."},
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
        print(result["text"])

    print("\n ANSWER:")
    print(response.output_text)

#answer_question("What problems are customers experiencing with the mobile app?")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  