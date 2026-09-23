from openai import OpenAI
import os
import json

client = OpenAI()

files = os.listdir("documents")
print(files)

#Ingestion Pipeline
#Read and Structure the data
chunks =[]
for filename in files :

    #Read the file
    filepath = os.path.join("documents",filename)
    with open(filepath,"r") as file:
        content = file.read()

    #Split the content into sections and chunk them with their titles
    file_sections = content.split("\n\n")
    formatted_filesections = []
    stop = len(file_sections)
    for i in range(1,stop,2):
        formatted_filesections.append(
            file_sections[i] + "\n" + file_sections[i+1]
        )

    #Add each chunked section from all the different files into one big chunk file along with their source
    for formatted_filesection in formatted_filesections:
        chunks.append(
            {
                "source" : filename,
                "text" : formatted_filesection
            }
        )

#Create embeddings for the data
chunk_embeddings = []
for chunk in chunks : 
    #embed the chunk 
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input = chunk["text"]
    )
    chunk_embedding = response.data[0].embedding

    chunk_embeddings.append(
            {
                "source" : chunk["source"],
                "text" : chunk["text"],
                "embedding" : chunk_embedding
            }
    )

#Save the embeddings for future use
with open("knowledge_base.json", "w") as file : 
    json.dump(chunk_embeddings,file)



