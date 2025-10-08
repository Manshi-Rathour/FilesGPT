from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
from ..core.config import settings
import traceback
from pinecone import Pinecone

router = APIRouter(prefix="/history", tags=["History"])

# ---------- Pinecone Setup ----------
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

# ---------- Schemas ----------
class Message(BaseModel):
    sender: str
    text: str

class ChatHistory(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    email: Optional[str] = None
    pdf_name: Optional[str] = None
    document_id: Optional[str] = None
    messages: List[Message] = []
    created_at: str

    class Config:
        allow_population_by_field_name = True

# ---------- Mongo Client ----------
_mongo_client_h = None
def get_mongo_client():
    global _mongo_client_h
    if _mongo_client_h is None:
        print("[DEBUG] Initializing MongoDB client...")
        _mongo_client_h = MongoClient(settings.MONGO_URI)
    return _mongo_client_h

# ---------- Routes ----------
@router.get("/user/{user_id}", response_model=List[ChatHistory])
async def get_user_chats(user_id: str, limit: int = 50):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")

        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        history_col = db["history"]

        docs = list(
            history_col.find({"user_id": ObjectId(user_id)})
            .sort("created_at", -1)
            .limit(limit)
        )

        normalized = []
        for d in docs:
            normalized.append({
                "_id": str(d["_id"]),
                "user_id": str(d["user_id"]),
                "email": d.get("email", ""),
                "pdf_name": d.get("pdf_name", ""),
                "document_id": str(d.get("document_id")) if d.get("document_id") else None,
                "messages": d.get("messages", []),
                "created_at": d["created_at"].isoformat() if isinstance(d.get("created_at"), datetime) else str(d.get("created_at", ""))
            })

        return normalized

    except Exception:
        print("[ERROR] Exception in get_user_chats:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{chat_id}", status_code=204)
async def delete_chat(chat_id: str):
    """
    Delete a single chat and all associated records from:
    - history collection
    - uploads collection
    - Pinecone index
    """
    try:
        if not ObjectId.is_valid(chat_id):
            raise HTTPException(status_code=400, detail="Invalid chat ID")

        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        history_col = db["history"]
        uploads_col = db["uploads"]

        # Find chat record
        chat = history_col.find_one({"_id": ObjectId(chat_id)})
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        user_id = str(chat.get("user_id"))
        document_id = str(chat.get("document_id"))

        # Delete from Pinecone
        try:
            index.delete(delete_all=False, filter={"user_id": user_id, "document_id": document_id})
            print(f"[INFO] Deleted Pinecone vectors for doc {document_id}")
        except Exception as e:
            print(f"[WARN] Pinecone deletion failed: {e}")

        # Delete from uploads collection
        uploads_col.delete_one({"_id": ObjectId(document_id)})

        # Delete from history collection
        history_col.delete_one({"_id": ObjectId(chat_id)})

        print(f"[INFO] Deleted chat {chat_id}, document {document_id}, user {user_id}")
        return {"message": "Chat deleted successfully"}

    except HTTPException:
        raise
    except Exception:
        print("[ERROR] Exception in delete_chat:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
