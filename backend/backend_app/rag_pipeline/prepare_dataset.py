from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from ..core.config import settings
from typing import List, Dict
import torch

device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

EMBEDDER_MODEL = "intfloat/e5-large-v2"
embedder = SentenceTransformer(EMBEDDER_MODEL, device=device)
EMBEDDINGS_DIM = embedder.get_sentence_embedding_dimension()

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
if settings.PINECONE_INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=settings.PINECONE_INDEX,
        dimension=EMBEDDINGS_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(settings.PINECONE_INDEX)

def chunk_text_to_chunks(text: str, source: str, user_id: str, document_id: str) -> List[Dict]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150, separators=["\n\n", "\n", " ", ""])
    chunks = splitter.split_text(text)
    out = []
    for i, chunk in enumerate(chunks):
        out.append({
            "id": f"{user_id}-{document_id}-{i}",
            "text": chunk,
            "metadata": {"user_id": user_id, "document_id": document_id, "source": source, "chunk_id": i, "content": chunk}
        })
    return out

def embed_and_upsert(chunks: List[Dict], batch_size: int = 64):
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start+batch_size]
        vectors = embedder.encode([c["text"] for c in batch], convert_to_numpy=True, show_progress_bar=False)
        upsert_items = [(c["id"], v.tolist(), c["metadata"]) for c, v in zip(batch, vectors)]
        index.upsert(vectors=upsert_items)

def process_and_store(text: str, user_id: str, source: str, document_id: str) -> int:
    chunks = chunk_text_to_chunks(text, source=source, user_id=user_id, document_id=document_id)
    embed_and_upsert(chunks)
    return len(chunks)
