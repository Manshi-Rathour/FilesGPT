import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from ..core.config import settings
from typing import List, Dict
import torch

# --- Initialize device for sentence-transformers ---
device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

# --- Load embedder once (module-level) ---
EMBEDDER_MODEL = "intfloat/e5-large-v2"
print(f"Loading embedding model {EMBEDDER_MODEL} on device {device}...")
embedder = SentenceTransformer(EMBEDDER_MODEL, device=device)
EMBEDDINGS_DIM = embedder.get_sentence_embedding_dimension()
print(f"Embedder ready. Dimension = {EMBEDDINGS_DIM}")

# --- Initialize Pinecone v3 client ---
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Ensure index exists
if settings.PINECONE_INDEX not in pc.list_indexes().names():
    print(f"Creating Pinecone index {settings.PINECONE_INDEX} (dim={EMBEDDINGS_DIM})")
    pc.create_index(
        name=settings.PINECONE_INDEX,
        dimension=EMBEDDINGS_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # adjust region if needed
    )

index = pc.Index(settings.PINECONE_INDEX)


def chunk_text_to_chunks(text: str, source: str, user_id: str) -> List[Dict]:
    """
    Splits text into chunks and returns a list of chunk dicts with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    out = []
    for i, chunk in enumerate(chunks):
        out.append({
            "id": f"{user_id}-{os.path.basename(source)}-{i}",
            "text": chunk,
            "metadata": {
                "user_id": user_id,
                "source": source,
                "chunk_id": i
            }
        })
    return out


def embed_and_upsert(chunks: List[Dict], batch_size: int = 64):
    """
    Generate embeddings for chunk texts in batches and upsert to Pinecone.
    Each upsert item must be: (id, vector, metadata)
    """
    if not chunks:
        return

    total = len(chunks)
    for start in range(0, total, batch_size):
        batch = chunks[start:start+batch_size]
        texts = [c["text"] for c in batch]
        vectors = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        upsert_items = []
        for c, vec in zip(batch, vectors):
            upsert_items.append((c["id"], vec.tolist(), c["metadata"]))
        # Upsert to Pinecone
        index.upsert(vectors=upsert_items)
        print(f"Upserted {len(upsert_items)} vectors (batch {start // batch_size + 1})")


def process_and_store(text: str, user_id: str, source: str) -> int:
    """
    Full pipeline: chunk text, embed, and upsert to Pinecone.
    Returns number of chunks upserted.
    """
    chunks = chunk_text_to_chunks(text, source=source, user_id=user_id)
    embed_and_upsert(chunks)
    return len(chunks)
