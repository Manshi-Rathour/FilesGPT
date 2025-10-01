from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.auth import router as auth_router
from .api.pdf import router as pdf_router
from .api.query import router as query_router
from .api.history import router as history_router
# from .api.feedback import router as feedback_router

# Initialize FastAPI app
app = FastAPI(title=settings.PROJECT_NAME)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(pdf_router)
app.include_router(query_router)
app.include_router(history_router)
# app.include_router(feedback_router)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
