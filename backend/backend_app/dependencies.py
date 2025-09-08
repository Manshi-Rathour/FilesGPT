from fastapi import Header, HTTPException

async def get_api_version(x_api_version: str | None = Header(None)):
    return x_api_version or "1"
