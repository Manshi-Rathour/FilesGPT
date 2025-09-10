from fastapi import APIRouter, HTTPException, Depends
from ..core.config import settings
from pymongo import MongoClient
from typing import List
from datetime import datetime

router = APIRouter(prefix="/history", tags=["History"])

_mongo_client_h = None
def get_mongo_client():
    global _mongo_client_h
    if _mongo_client_h is None:
        _mongo_client_h = MongoClient(settings.MONGO_URI)
    return _mongo_client_h

@router.get("/{user_id}", response_model=List[dict])
async def get_history(user_id: str, limit: int = 50):
    """
    Returns the last `limit` history entries for a user (most recent first)
    """
    try:
        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        history_col = db["history"]
        docs = list(history_col.find({"user_id": user_id}).sort("created_at", -1).limit(limit))
        # convert ObjectId and datetime to strings (simple conversion)
        for d in docs:
            d["_id"] = str(d["_id"])
            if isinstance(d.get("created_at"), datetime):
                d["created_at"] = d["created_at"].isoformat()
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
