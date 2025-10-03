from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
from ..core.config import settings
import traceback

router = APIRouter(prefix="/history", tags=["History"])

# ---------- Schemas ----------
class Message(BaseModel):
    sender: str
    text: str

class ChatHistory(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    email: Optional[str] = None
    pdf_name: Optional[str] = None
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

        # Normalize for frontend
        normalized = []
        for d in docs:
            normalized.append({
                "_id": str(d["_id"]),
                "user_id": str(d["user_id"]),
                "email": d.get("email", ""),
                "pdf_name": d.get("pdf_name", ""),
                "messages": d.get("messages", []),
                "created_at": d["created_at"].isoformat() if isinstance(d.get("created_at"), datetime) else str(
                    d.get("created_at", ""))
            })

        # print("[DEBUG] Normalized docs before return:", normalized)
        return normalized

    except Exception:
        print("[ERROR] Exception in get_user_chats:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{chat_id}", response_model=ChatHistory)
async def get_chat(chat_id: str):
    try:
        if not ObjectId.is_valid(chat_id):
            raise HTTPException(status_code=400, detail="Invalid chat ID")

        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        history_col = db["history"]

        doc = history_col.find_one({"_id": ObjectId(chat_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Normalize single chat for frontend
        normalized = {
            "_id": str(doc["_id"]),
            "user_id": str(doc.get("user_id", "")),
            "email": doc.get("email", ""),
            "pdf_name": doc.get("pdf_name", ""),
            "messages": doc.get("messages", []),
            "created_at": doc.get("created_at").isoformat() if isinstance(doc.get("created_at"), datetime) else str(doc.get("created_at", ""))
        }

        # print("[DEBUG] Normalized single chat:", normalized)
        return normalized

    except HTTPException:
        raise
    except Exception:
        print("[ERROR] Exception in get_chat:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
