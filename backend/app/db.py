from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from .config import settings

_client: AsyncIOMotorClient | None = None


def _client_kwargs() -> dict:
    """Atlas (mongodb+srv) needs TLS; point it at certifi's CA bundle so the
    certificate verifies even when the system trust store is incomplete."""
    try:
        import certifi

        return {"tls": True, "tlsCAFile": certifi.where()}
    except ImportError:
        return {}


async def connect() -> None:
    """Open the Mongo connection and ensure indexes. Called on app startup."""
    global _client
    _client = AsyncIOMotorClient(settings.MONGO_URI, **_client_kwargs())
    await users().create_index("email", unique=True)
    await uploads().create_index("user_id")
    await chats().create_index([("user_id", 1), ("created_at", -1)])


async def disconnect() -> None:
    """Close the Mongo connection. Called on app shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def db() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("Database not connected")
    return _client[settings.MONGO_DB_NAME]


def users() -> AsyncIOMotorCollection:
    return db()["users"]


def uploads() -> AsyncIOMotorCollection:
    return db()["uploads"]


def chats() -> AsyncIOMotorCollection:
    return db()["history"]
