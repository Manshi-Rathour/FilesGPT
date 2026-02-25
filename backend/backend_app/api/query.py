from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.config import settings
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import torch
import requests
import asyncio
from typing import List

router = APIRouter(prefix="/query", tags=["Query"])


# Device Setup (MPS / CUDA / CPU)

device = (
    "mps" if torch.backends.mps.is_available()
    else "cuda" if torch.cuda.is_available()
    else "cpu"
)

EMBEDDER_MODEL = "intfloat/e5-large-v2"
embedder = SentenceTransformer(EMBEDDER_MODEL, device=device)


# Pinecone Setup

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)


# Request / Response Models

class QueryRequest(BaseModel):
    question: str
    document_id: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str



# Ollama LLM Call

def call_llm_chat(system_prompt: str, user_prompt: str) -> str:
    try:
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "options": {
                    "temperature": 0.0,
                    "num_predict": 600,
                    "num_ctx": 8192,
                },
                "stream": False,
            },
            timeout=180,
        )

        response.raise_for_status()
        data = response.json()

        if "message" not in data or "content" not in data["message"]:
            raise ValueError("Invalid response from Ollama")

        return data["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")



# Main Query Endpoint

@router.post("/", response_model=QueryResponse)
async def query_pdf_endpoint(request: QueryRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # IMPORTANT for E5 models
        formatted_query = f"query: {request.question}"

        # Run embedding in thread (prevents blocking)
        q_vec = await asyncio.to_thread(
            embedder.encode,
            formatted_query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # Query Pinecone
        query_resp = index.query(
            vector=q_vec.tolist(),
            top_k=request.top_k,
            include_metadata=True,
            filter={"document_id": {"$eq": request.document_id}},
        )

        matches = query_resp.get("matches", [])

        if not matches:
            return {
                "answer": "No relevant results found for this document."
            }

        # Collect matched context
        contexts: List[str] = [
            m["metadata"].get("content", "")
            for m in matches if m.get("metadata")
        ]

        combined_context = "\n\n".join(contexts)

        system_prompt = """
You are a precise and grounded AI assistant.
Answer ONLY using the provided context.

If the answer is not explicitly present, respond exactly:
"The provided data does not contain enough information to answer this question."
Do not explain further.
"""

        user_prompt = f"""
Context:
{combined_context}

Question:
{request.question}

Answer using only the context above.
"""

        # Call Ollama safely
        answer_text = await asyncio.to_thread(
            call_llm_chat,
            system_prompt,
            user_prompt
        )

        print(f"Final Answer:")
        print(answer_text)

        return {"answer": answer_text}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")