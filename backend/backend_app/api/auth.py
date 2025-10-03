from datetime import datetime
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Response
from fastapi.security import OAuth2PasswordRequestForm
import cloudinary.uploader

from ..core.config import settings
from ..core.auth import create_access_token, get_current_user, hash_password, verify_password
from ..db.mongodb import users_col, uploads_col, history_col
from ..db.models import UserPublic, Token

# Pinecone setup
from pinecone import Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

router = APIRouter(tags=["Auth"])

# Cloudinary config
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def map_user_public(doc: dict) -> UserPublic:
    return UserPublic(
        id=str(doc["_id"]),
        name=doc["name"],
        email=doc["email"],
        avatar_url=doc.get("avatar_url"),
        created_at=doc["created_at"],
    )


# ---- Signup ----
@router.post("/signup", response_model=UserPublic, status_code=201)
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    avatar: Optional[UploadFile] = File(None),
):
    col = users_col()
    if await col.find_one({"email": email.lower().strip()}):
        raise HTTPException(status_code=409, detail="Email already registered.")

    avatar_url = None
    if avatar:
        up = cloudinary.uploader.upload(
            avatar.file, folder="pdfGpt/users", resource_type="image", use_filename=True, unique_filename=True
        )
        avatar_url = up.get("secure_url")

    doc = {
        "name": name.strip(),
        "email": email.lower().strip(),
        "password_hash": hash_password(password),
        "avatar_url": avatar_url,
        "created_at": datetime.utcnow(),
    }
    result = await col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return map_user_public(doc)


# ---- Login ----
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username.lower().strip()
    password = form_data.password

    col = users_col()
    user = await col.find_one({"email": email})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    token = create_access_token(sub=email)
    return Token(access_token=token)


# ---- Get current user ----
@router.get("/me", response_model=UserPublic)
async def get_me(current_user: dict = Depends(get_current_user)):
    return map_user_public(current_user)


# ---- Update profile ----
@router.put("/me", response_model=UserPublic)
async def update_me(
    name: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    new_avatar: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
):
    col = users_col()
    update = {}

    if name:
        update["name"] = name.strip()
    if password:
        update["password_hash"] = hash_password(password)
    if new_avatar:
        up = cloudinary.uploader.upload(
            new_avatar.file, folder="pdfGpt/users", resource_type="image", use_filename=True, unique_filename=True
        )
        update["avatar_url"] = up.get("secure_url")

    if update:
        await col.update_one({"_id": ObjectId(current_user["_id"])}, {"$set": update})
        current_user.update(update)

    return map_user_public(current_user)


# ---- Delete account ----
@router.delete("/me", status_code=204)
async def delete_me(current_user: dict = Depends(get_current_user)):
    from bson import ObjectId
    from fastapi import Response

    # Ensure user_id is ObjectId
    user_id = current_user["_id"]
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    # Pinecone
    try:
        index.delete(delete_all=False, filter={"user_id": str(user_id)})
    except Exception as e:
        print("Pinecone delete warning:", e)

    # Delete uploads
    try:
        up_col = uploads_col()
        await up_col.delete_many({"user_id": str(user_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete uploads: {e}")

    # Delete chat history
    try:
        hist_col = history_col()
        await hist_col.delete_many({"user_id": user_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete history: {e}")

    # Delete user document
    try:
        usr_col = users_col()
        await usr_col.delete_one({"_id": user_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {e}")

    return Response(status_code=204)
