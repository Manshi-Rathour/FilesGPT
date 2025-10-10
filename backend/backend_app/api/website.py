from fastapi import APIRouter, HTTPException, Depends, Form
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from ..core.config import settings
from ..core.auth import get_current_user
from ..rag_pipeline.website_loader import extract_text_from_website
from ..rag_pipeline.prepare_dataset import process_and_store
import uuid
import os

router = APIRouter(prefix="/website", tags=["Website"])

_mongo_client = None


def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGO_URI)
    return _mongo_client


UPLOAD_DIR = "backend_app/rag_pipeline/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload/")
async def upload_website(
    url: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a website URL, extract text, process & store embeddings in Pinecone.
    """
    if not url:
        raise HTTPException(status_code=400, detail="No URL provided")

    try:
        print(f"[DEBUG] Starting website upload for user {current_user['_id']} and URL: {url}")

        # Step 1: Extract text from website
        text = extract_text_from_website(url)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No readable text found at the given URL.")
        print(f"[DEBUG] Successfully extracted {len(text)} characters")

        # Step 2: Save a placeholder "stored_as" file for consistency
        # (so both PDF and website uploads have a local stored file)
        filename = f"{uuid.uuid4().hex}_website.txt"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Step 3: Mongo setup
        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        uploads = db["uploads"]

        # Step 4: Insert metadata
        result = uploads.insert_one({
            "user_id": ObjectId(current_user["_id"]),
            "email": current_user["email"],
            "filename": url,
            "stored_as": file_path,
            "chunks_upserted": 0,
            "created_at": datetime.utcnow()
        })
        document_id = str(result.inserted_id)
        print(f"[DEBUG] Created document with ID: {document_id}")

        # Step 5: Embed & store
        chunk_count = process_and_store(
            text,
            user_id=str(current_user["_id"]),
            document_id=document_id,
            source=url
        )
        print(f"[DEBUG] Successfully processed {chunk_count} chunks")

        # Step 6: Update metadata
        uploads.update_one(
            {"_id": result.inserted_id},
            {"$set": {"chunks_upserted": chunk_count}}
        )

        print(f"[DEBUG] Website upload completed successfully")
        return {
            "status": "success",
            "message": f"Processed text from {url}",
            "chunks": chunk_count,
            "document_id": document_id
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Website upload failed: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Website upload failed: {str(e)}")
