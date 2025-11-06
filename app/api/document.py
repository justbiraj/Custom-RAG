from fastapi import APIRouter, UploadFile, Form


router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile, description: str = Form(...)):
    """
    Endpoint to upload a document with a description.
    """
    """
    *TODO: Implement the logic to handle the uploaded file and description.
    1.Extract file content
    2.chunk the content 
    3.create embeddings
    4.store in vector db
    5.return success response
    6.handle errors appropriately
    """
    pass
    # content = await file.read()

    # Here you would typically save the file and description to a database or storage
    # return {"filename": file.filename, "description": description, "size": len(content)}