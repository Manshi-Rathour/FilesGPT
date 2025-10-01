from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from ..core.config import settings
from pymongo import MongoClient
from ..core.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

# Mongo client
_mongo_client = None
def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGO_URI)
    return _mongo_client

# Request model
class SaveHistoryRequest(BaseModel):
    messages: list  # [{sender: "user"/"bot", text: "..."}]

@router.post("/save/")
async def save_chat_history(
    request: SaveHistoryRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # print("DEBUG - current_user:", current_user)
        # print("DEBUG - messages:", request.messages)

        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        history_col = db["history"]

        history_col.insert_one({
            "user_id": str(current_user["_id"]),
            "email": current_user["email"],
            "messages": request.messages,
            "created_at": datetime.utcnow()
        })

        return {"status": "success", "message": "Chat history saved"}
    except Exception as e:
        print("DEBUG - error:", e)
        raise HTTPException(status_code=500, detail=str(e))
