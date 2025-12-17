from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # <--- NEW IMPORT

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Define the shape of the data we expect
class UserInput(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"message": "IT WORKS! The Python Backend is running."}

# 2. Create a POST route to receive data
@app.post("/api/chat")
def chat_with_python(user_input: UserInput):
    # This is where you would put AI logic later
    received_text = user_input.message
    return {"reply": f"Python received your message: '{received_text}'"}