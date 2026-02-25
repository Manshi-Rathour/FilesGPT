from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from ..core.config import settings
from ..core.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

_mongo_client = None
def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGO_URI)
    return _mongo_client

# Request model
class SaveHistoryRequest(BaseModel):
    pdf_name: str
    document_id: str
    messages: list

@router.post("/save/")
async def save_chat_history(
    request: SaveHistoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Save chat messages to MongoDB, linking each chat to uploaded PDF by document_id.
    """
    try:
        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        history_col = db["history"]

        history_doc = {
            "user_id": ObjectId(current_user["_id"]),
            "email": current_user["email"],
            "pdf_name": request.pdf_name,
            "document_id": ObjectId(request.document_id),
            "messages": request.messages,
            "created_at": datetime.utcnow()
        }

        result = history_col.insert_one(history_doc)

        return {
            "status": "success",
            "message": "Chat history saved and linked to PDF",
            "chat_id": str(result.inserted_id)
        }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
