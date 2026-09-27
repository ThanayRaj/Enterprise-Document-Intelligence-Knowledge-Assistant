"""Semantic retrieval over the FAISS index."""

from __future__ import annotations

from typing import Any

from src.config import DEFAULT_TOP_K, MIN_SIMILARITY
from src.embeddings import embed_query
from src.vector_store import VectorStore, hits_to_records


def retrieve(
    question: str,
    store: VectorStore,
    chunks_by_id: dict[int, dict[str, Any]],
    top_k: int = DEFAULT_TOP_K,
    min_similarity: float = MIN_SIMILARITY,
) -> list[dict[str, Any]]:
    question = (question or "").strip()
    if not question or store.is_empty():
        return []
    query_vec = embed_query(question)
    hits = store.search(query_vec, top_k=top_k)
    records = hits_to_records(hits, chunks_by_id)
    return [r for r in records if r.get("score", 0.0) >= min_similarity]
