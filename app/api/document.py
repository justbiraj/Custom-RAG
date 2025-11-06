from fastapi import APIRouter, UploadFile, Form, Depends
from sqlalchemy.orm import Session
from app.services import extractor, chunker, embedding
from app.core.vector_client import VectorDB
from app.core.database import get_db, Document
from app.core.config import OLLAMA_EMBED_MODEL

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile,
    chunk_strategy: str = Form("recursive"),
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    VectorDB_instance = VectorDB(session_id)
    text = extractor.extract_text_from_pdf(file)
    chunks = chunker.chunk_text(text, strategy=chunk_strategy)
    embeddings = embedding.create_ollama_embedding(chunks)
    VectorDB_instance.upsert(chunks, embeddings)

    new_doc = Document(
        filename=file.filename,
        chunk_strategy=chunk_strategy,
        embedding_model=OLLAMA_EMBED_MODEL,
        session_id=session_id
    )
    db.add(new_doc)
    db.commit()
    
    return {"status": "success", "chunks": len(chunks)}
