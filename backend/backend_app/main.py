from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.auth import router as auth_router
from .api.pdf import router as pdf_router
from .api.query import router as query_router
from .api.history import router as history_router
from .api.save_history import router as save_history_router

# Initialize FastAPI app
app = FastAPI(title=settings.PROJECT_NAME)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.CLIENT_URL,        # production frontend URL
        "http://localhost:5173",    # local dev frontend
        "http://127.0.0.1:5173",    # sometimes axios uses 127.0.0.1
    ],
    allow_credentials=True,
    allow_methods=["*"],          # allow GET, POST, PUT, DELETE etc.
    allow_headers=["*"],          # allow all headers (Authorization, Content-Type)
)


# Register routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(pdf_router)
app.include_router(query_router)
app.include_router(history_router)         # GET /history endpoints
app.include_router(save_history_router)    # POST /chat/save/ endpoint

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
