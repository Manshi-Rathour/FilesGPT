from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
import cloudinary
import cloudinary.uploader

from backend.backend_app.core.config import settings
from backend.backend_app.core.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.backend_app.db.mongodb import users_col
from backend.backend_app.db.models import (
    UserCreate, UserLogin, UserPublic, Token, ProfileUpdate
)

router = APIRouter(tags=["Auth"])

# Configure Cloudinary once
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

@router.post("/signup", response_model=UserPublic, status_code=201)
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    avatar: Optional[UploadFile] = File(None),
):
    col = users_col()

    # check duplicate email
    if await col.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="Email already registered.")

    avatar_url: Optional[str] = None
    if avatar:
        try:
            up = cloudinary.uploader.upload(
                avatar.file,
                folder="pdfGpt/users",
                resource_type="image",
                use_filename=True,
                unique_filename=True,
            )
            avatar_url = up.get("secure_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")

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

@router.get("/me", response_model=UserPublic)
async def get_me(current_user: dict = Depends(get_current_user)):
    return map_user_public(current_user)

@router.put("/me", response_model=UserPublic)
async def update_me(
    payload: ProfileUpdate = Depends(),
    new_avatar: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
):
    col = users_col()
    update: dict = {}

    if payload.name is not None:
        update["name"] = payload.name.strip()

    if new_avatar:
        try:
            up = cloudinary.uploader.upload(
                new_avatar.file,
                folder="pdfGpt/users",
                resource_type="image",
                use_filename=True,
                unique_filename=True,
            )
            update["avatar_url"] = up.get("secure_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")

    if not update:
        return map_user_public(current_user)

    await col.update_one({"_id": current_user["_id"]}, {"$set": update})
    current_user.update(update)
    return map_user_public(current_user)

@router.delete("/me", status_code=204)
async def delete_me(current_user: dict = Depends(get_current_user)):
    col = users_col()
    await col.delete_one({"_id": current_user["_id"]})
    return None
