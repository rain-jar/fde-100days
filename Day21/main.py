from fastapi import FastAPI
from pydantic import BaseModel
from app import process_request

app = FastAPI()


#Create a pydantic model for Frontend Requests
class ChatRequest(BaseModel):
    message: str

#Creating API Response model
class ChatResponse(BaseModel):
    answer: str
    trace_id: str

#Creating a GET endpoint at /health and return a message
@app.get("/health")
async def health():
    return{"status":"ok"}

#API POST endpoint calls the Agent
@app.post("/chat", response_model=ChatResponse)

async def chat(request: ChatRequest):
    result = process_request(request.message)

    return {
        "answer": result["response"]["answer"],
        "trace_id": result["trace_id"]
    }

