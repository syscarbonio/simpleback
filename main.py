from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class EmailPayload(BaseModel):
    email: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.post("/submit-email")
async def submit_email(payload: EmailPayload):
    async with httpx.AsyncClient() as client:
        # Check if email already exists
        existing_email_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/subscribers",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
            params={
                "select": "email",
                "email": f"eq.{payload.email}"
            }
        )
        
        if existing_email_response.status_code != 200:
            raise HTTPException(status_code=existing_email_response.status_code, detail="Error checking existing email")
        
        existing_emails = existing_email_response.json()
        if existing_emails:
            return {"message": "Hey! Your email is already here!"}
        
        # Insert new email
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/subscribers",
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            json={"email": payload.email}
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
    return {"message": "Email submitted successfully"}
