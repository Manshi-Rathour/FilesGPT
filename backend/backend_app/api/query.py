from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.config import settings
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import openai
import torch

router = APIRouter(prefix="/query", tags=["Query"])

# Device setup and model loading
device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
EMBEDDER_MODEL = "intfloat/e5-large-v2"
embedder = SentenceTransformer(EMBEDDER_MODEL, device=device)

# Pinecone setup
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

# OpenAI setup
openai.api_key = settings.OPENAI_API_KEY

# Request / Response Models
class QueryRequest(BaseModel):
    question: str
    document_id: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str

# OpenAI helper
def call_openai_chat(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=800
    )
    return resp.choices[0].message.content.strip()


@router.post("/", response_model=QueryResponse)
async def query_pdf_endpoint(request: QueryRequest):
    try:
        # Encode the query into vector
        q_vec = embedder.encode(request.question, convert_to_numpy=True).tolist()

        # Query Pinecone for top relevant chunks
        query_resp = index.query(
            vector=q_vec,
            top_k=request.top_k,
            include_metadata=True,
            filter={"document_id": {"$eq": request.document_id}}
        )

        matches = query_resp.get("matches", [])
        if not matches:
            return {"answer": f"No relevant results found for document {request.document_id}."}

        # Collect matched context text
        contexts = [m["metadata"].get("content", "") for m in matches]

        # Strong grounding prompt
        system_prompt = """
You are a precise and grounded AI assistant that must answer ONLY using the information provided in the given context.

- The context may come from PDFs, images (OCR text), Word documents, or website data — but do NOT get confused by mentions of "PDF", "image", "document", or "website" in the question. These are simply sources of the text already included in the context.
- Never use any external knowledge, assumptions, or general facts outside the provided context.
- If the context does not contain enough information to answer accurately, respond with:
  "The provided data does not contain enough information to answer this question."

Guidelines:
1. Use only the context below to answer.
2. Do not invent, guess, or elaborate beyond what is explicitly stated.
3. Be concise and factual.
4. Ignore duplicate or irrelevant segments in the context.

Your task: Read the context carefully and answer the user's question only if the answer exists within it.
"""

        user_prompt = f"""
Context:
{'\n\n'.join(contexts)}

Question: {request.question}

Answer strictly using only the above context.
"""

        # Call OpenAI to generate answer
        answer_text = call_openai_chat(system_prompt, user_prompt)

        return {"answer": answer_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))