from fastapi import FastAPI
from app.api import document, chat
from app.core.database import init_db

app = FastAPI(title="RAG Backend (Ollama + Gemini)", version="1.0")

app.include_router(document.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.on_event("startup")
async def startup_event():
    init_db()
    
