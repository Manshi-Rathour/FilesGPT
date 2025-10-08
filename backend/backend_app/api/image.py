from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os, shutil, uuid
from ..core.config import settings
from ..core.auth import get_current_user
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from ..rag_pipeline.image_loader import extract_text_from_image_file, extract_text_from_pdf_bytes
from ..rag_pipeline.prepare_dataset import process_and_store

router = APIRouter(prefix="/image", tags=["Image"])

_mongo_client = None
def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGO_URI)
    return _mongo_client

UPLOAD_DIR = "backend_app/rag_pipeline/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        # Save uploaded file
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        source = file.filename

        # Determine file type
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext in ["png", "jpg", "jpeg"]:
            # Single image
            text = extract_text_from_image_file(file_path)
        elif file_ext == "pdf":
            # PDF containing images
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
            text = extract_text_from_pdf_bytes(pdf_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload image or PDF.")

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the provided file")

        # Log upload to MongoDB
        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        uploads = db["uploads"]

        result = uploads.insert_one({
            "user_id": ObjectId(current_user["_id"]),
            "email": current_user["email"],
            "filename": source,
            "stored_as": file_path,
            "chunks_upserted": 0,
            "created_at": datetime.utcnow()
        })
        document_id = str(result.inserted_id)

        # Process & store in Pinecone
        chunk_count = process_and_store(
            text,
            user_id=str(current_user["_id"]),
            document_id=document_id,
            source=source
        )
        uploads.update_one({"_id": result.inserted_id}, {"$set": {"chunks_upserted": chunk_count}})

        return {"status": "success", "message": f"Processed {source}", "chunks": chunk_count, "document_id": document_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
