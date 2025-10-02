from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import os, shutil, uuid
from ..rag_pipeline.pdf_loader import download_file_from_url, extract_text_from_url_maybe_html
from ..rag_pipeline.prepare_dataset import process_and_store
from ..core.config import settings
from ..core.auth import get_current_user
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/pdf", tags=["PDF"])

# simple pymongo client (module-level)
_mongo_client = None
def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGO_URI)
    return _mongo_client

UPLOAD_DIR = "backend_app/rag_pipeline/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload/")
async def upload_pdf(
    file: UploadFile = File(None),
    url: str = Form(None),
    current_user: dict = Depends(get_current_user)   # ✅ pull real user
):
    """
    Accept either a PDF file upload or a URL (pointing to PDF or HTML).
    Process it and store embeddings in Pinecone.
    Also logs upload metadata into MongoDB collection `uploads`.
    """
    if not file and not url:
        raise HTTPException(status_code=400, detail="Provide file or url")

    try:
        # Prepare file path
        if file:
            filename = f"{uuid.uuid4().hex}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            content_type = "application/pdf"  # trust upload
            source = file.filename
        else:
            parsed_name = os.path.basename(url.split("?")[0]) or f"downloaded_{uuid.uuid4().hex}.pdf"
            filename = f"{uuid.uuid4().hex}_{parsed_name}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            content_type, file_path = download_file_from_url(url, file_path)
            source = url

        # extract text (PDF or HTML fallback)
        text = extract_text_from_url_maybe_html(file_path, content_type)

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the provided file/URL")

        # Process: chunk + embed + upsert to Pinecone
        chunk_count = process_and_store(text, user_id=str(current_user["_id"]), source=source)

        # Log upload metadata to MongoDB
        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        uploads = db["uploads"]
        uploads.insert_one({
            "user_id": ObjectId(current_user["_id"]),   # ✅ ObjectId like in chat
            "email": current_user["email"],
            "filename": source,
            "stored_as": file_path,
            "chunks_upserted": chunk_count,
            "created_at": datetime.utcnow()
        })

        return {"status": "success", "message": f"Processed {source}", "chunks": chunk_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
