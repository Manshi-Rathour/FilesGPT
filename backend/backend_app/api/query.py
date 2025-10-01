from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..core.config import settings
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import openai
from datetime import datetime
import torch

router = APIRouter(prefix="/query", tags=["Query"])

# --- Setup embedder ---
device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
EMBEDDER_MODEL = "intfloat/e5-large-v2"
embedder = SentenceTransformer(EMBEDDER_MODEL, device=device)

# --- Pinecone v3 client ---
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

# --- OpenAI client ---
openai.api_key = settings.OPENAI_API_KEY

# --- Mongo client ---
_mongo_client_q = None
def get_mongo_client():
    global _mongo_client_q
    if _mongo_client_q is None:
        _mongo_client_q = MongoClient(settings.MONGO_URI)
    return _mongo_client_q

# --- Pydantic models ---
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

# --- OpenAI helper ---
def call_openai_chat(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.0,
        max_tokens=800
    )
    return resp["choices"][0]["message"]["content"].strip()

# --- API endpoint ---
@router.post("/", response_model=QueryResponse)
async def query_pdf_endpoint(request: QueryRequest, user_id: str = "anonymous"):
    try:
        # 1) Embed question
        q_vec = embedder.encode(request.question, convert_to_numpy=True).tolist()

        # 2) Query Pinecone v3
        query_resp = index.query(vector=q_vec, top_k=request.top_k, include_metadata=True)
        matches = query_resp.get("matches", [])
        if not matches:
            return {"answer": "No relevant documents found.", "sources": []}

        # 3) Gather contexts and sources
        contexts = []
        sources = []
        for m in matches:
            meta = m.get("metadata", {}) or {}
            content = meta.get("content") or meta.get("text") or f"[chunk id: {m.get('id')}]"
            contexts.append(content)
            sources.append(meta.get("source", "unknown"))

        # 4) Build prompt and call OpenAI
        system_prompt = (
            "You are a helpful assistant. Use only the provided context to answer. "
            "Cite the source(s) by including the source URL/filename in your answer in a 'Sources:' line."
        )
        user_prompt = f"Context:\n\n{'\n\n'.join(contexts)}\n\nQuestion: {request.question}\n\nAnswer concisely and include a Sources: list."
        answer_text = call_openai_chat(system_prompt, user_prompt)

        # 5) Store history in MongoDB
        client = get_mongo_client()
        db = client[settings.MONGO_DB_NAME]
        history_col = db["history"]
        history_col.insert_one({
            "user_id": user_id,
            "question": request.question,
            "answer": answer_text,
            "sources": sources,
            "created_at": datetime.utcnow()
        })

        return {"answer": answer_text, "sources": sources}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
