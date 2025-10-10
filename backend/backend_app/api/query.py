from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.config import settings
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import openai
import torch

router = APIRouter(prefix="/query", tags=["Query"])

device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
EMBEDDER_MODEL = "intfloat/e5-large-v2"
embedder = SentenceTransformer(EMBEDDER_MODEL, device=device)

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

openai.api_key = settings.OPENAI_API_KEY

class QueryRequest(BaseModel):
    question: str
    document_id: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str

def call_openai_chat(system_prompt: str, user_prompt: str) -> str:
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    resp = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.0, max_tokens=800)
    return resp.choices[0].message.content.strip()

@router.post("/", response_model=QueryResponse)
async def query_pdf_endpoint(request: QueryRequest):
    try:
        q_vec = embedder.encode(request.question, convert_to_numpy=True).tolist()
        query_resp = index.query(vector=q_vec, top_k=request.top_k, include_metadata=True,
                                 filter={"document_id": {"$eq": request.document_id}})
        matches = query_resp.get("matches", [])
        if not matches:
            return {"answer": f"No relevant results found for document {request.document_id}."}

        contexts = [m["metadata"].get("content", "") for m in matches]
        system_prompt = "You are a helpful assistant. Use ONLY the provided context to answer."
        user_prompt = f"Context:\n\n{'\n\n'.join(contexts)}\n\nQuestion: {request.question}\n\nAnswer concisely."

        answer_text = call_openai_chat(system_prompt, user_prompt)
        return {"answer": answer_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
