from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import project settings and routers
from backend.backend_app.core.config import settings
from backend.backend_app.api.auth import router as auth_router

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

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
