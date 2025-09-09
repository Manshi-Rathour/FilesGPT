from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

_client: AsyncIOMotorClient | None = None

def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
    return _client

def get_db():
    return get_client()[settings.MONGO_DB_NAME]

def users_col():
    return get_db()["users"]
