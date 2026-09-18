from openai import OpenAI
import numpy as np  #to use cosine similarity for similarity calculation

client = OpenAI()

A = "The payment page is completely broken."
B = "Customers are unable to complete checkout"
C = "Employees receive 20 vacation days per year"
D = "Users report that clicking Pay does nothing."

responseA = client.embeddings.create(
    model="text-embedding-3-small",
    input = A
)

responseB = client.embeddings.create(
    model="text-embedding-3-small",
    input = B
)

responseC = client.embeddings.create(
    model="text-embedding-3-small",
    input = C
)

responseD = client.embeddings.create(
    model="text-embedding-3-small",
    input = D
)

embeddingA = responseA.data[0].embedding
embeddingB = responseB.data[0].embedding
embeddingC = responseC.data[0].embedding
embeddingD = responseD.data[0].embedding


def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a) * np.linalg.norm(b))

similarityDA = cosine_similarity(embeddingD, embeddingA)
similarityDB = cosine_similarity(embeddingD,embeddingB)
similarityDC = cosine_similarity(embeddingD, embeddingC)

print("D to B", similarityDA)
print("D to A", similarityDB)
print("D to C", similarityDC)