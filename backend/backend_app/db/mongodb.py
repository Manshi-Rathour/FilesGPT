from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

_client = None

def get_client():
    global _client
    if _client is None:
        if not settings.MONGO_URI:
            raise Exception("MONGO_URI is empty! Check your .env")
        _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client

def get_db():
    return get_client()[settings.MONGO_DB_NAME]

def users_col():
    return get_db()["users"]

def history_col():
    return get_db()["history"]

def uploads_col():
    return get_db()["uploads"]
