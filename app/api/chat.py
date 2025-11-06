from fastapi import APIRouter
from app.services.rag_pipeline import generate_response

router = APIRouter()

@router.post("/ask")
async def ask(query: str, session_id: str):
    answer = await generate_response(query, session_id)
    return {"response": answer}
