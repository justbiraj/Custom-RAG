import PyMuPDF as fitz
from fastapi import UploadFile

def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract text content from an uploaded PDF file.
    """
    if file.filename.endwith('.pdf'):
        pdf_document = fitz.open(stream=file.file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in pdf_document])
    elif file.filename.endswith('.txt'):
        return (file.read()).decode('utf-8')
    else:
        raise ValueError("Unsupported file type. Only PDF and TXT are supported.")
