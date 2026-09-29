from openai import OpenAI
import os
import json
import numpy as np

client = OpenAI()

#INGESTION PIPELINE
files = os.listdir("knowledge")
print(files)

chunks = []
#Read and Structure the knowledge base
for filename in files : 
    #Read the file
    filepath = os.path.join("knowledge",filename)
    with open(filepath, "r") as file:
        content = file.read()

    #Create chunks
    #Split the content into sections and chunk them with their titles
    file_sections = content.split("\n\n")
    formatted_filesections = []
    stop = len(file_sections)
    for i in range(0,stop,2):
        formatted_filesections.append(
            file_sections[i] + "\n" + file_sections[i+1]
        )

    #Combined all the formatted sections into big chunk
    for formatted_filesection in formatted_filesections:
        chunks.append(
            {
                "source" : filename,
                "text" : formatted_filesection
            }
        )

#Create embeddings for each chunk
chunk_embeddings = []
for chunk in chunks:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk["text"]
    )
    chunk_embeddings.append(
        {
            "source" : chunk["source"],
            "text" : chunk["text"],
            "embedding" : response.data[0].embedding
        }
    )

#Store the embeddings in a json file
with open("knowledge_base.json","w") as file:
    json.dump(chunk_embeddings,file)