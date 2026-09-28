from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from app import process_request
from dotenv import load_dotenv
import os

load_dotenv()

#FOR USER AUTHENTICATION
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")
if not INTERNAL_API_KEY:
    raise RuntimeError("INTERNAL_API_KEY is not configured")

#FOR USER AUTHORIZATION
USERS = {
    "USER-101": {
        "role": "support_agent",
        "allowed_customers": ["Acme"]
    },
    "USER-102": {
        "role": "manager",
        "allowed_customers": ["Acme", "Globex"]
    }
}

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

async def chat(request: ChatRequest, 
               x_api_key: str | None = Header(default=None),
               x_user_id: str | None = Header(default=None)
            ):
    #check authentication of the user requesting
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid API key"
        )

    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail = "User identity required"
        )
    

    # call the agent.
    result = process_request(request.message,x_user_id)

    return {
        "answer": result["response"]["answer"],
        "trace_id": result["trace_id"]
    }


