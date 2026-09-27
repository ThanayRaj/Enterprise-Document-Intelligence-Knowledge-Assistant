"""FAISS vector index with chunk-id mapping stored beside the index files."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from src.config import EMBEDDING_DIMENSION, FAISS_IDMAP_PATH, FAISS_INDEX_PATH, ensure_runtime_dirs

logger = logging.getLogger(__name__)


class VectorStoreError(Exception):
    pass


class VectorStore:
    def __init__(self, dimension: int = EMBEDDING_DIMENSION) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunk_ids: list[int] = []

    @property
    def size(self) -> int:
        return int(self.index.ntotal)

    def is_empty(self) -> bool:
        return self.size == 0

    def add(self, embeddings: np.ndarray, chunk_ids: list[int]) -> None:
        if embeddings is None or len(embeddings) == 0:
            return
        if len(chunk_ids) != embeddings.shape[0]:
            raise VectorStoreError("Number of embeddings does not match number of chunk ids.")
        vectors = np.asarray(embeddings, dtype="float32")
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        if vectors.shape[1] != self.dimension:
            raise VectorStoreError(
                f"Embedding dimension {vectors.shape[1]} does not match index dimension {self.dimension}."
            )
        self.index.add(vectors)
        self.chunk_ids.extend(int(cid) for cid in chunk_ids)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[tuple[int, float]]:
        if self.is_empty():
            return []
        vector = np.asarray(query_embedding, dtype="float32").reshape(1, -1)
        k = max(1, min(top_k, self.size))
        scores, indices = self.index.search(vector, k)
        results: list[tuple[int, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunk_ids):
                continue
            results.append((self.chunk_ids[idx], float(score)))
        return results

    def save(self, index_path: Path | None = None, idmap_path: Path | None = None) -> None:
        ensure_runtime_dirs()
        index_path = index_path or FAISS_INDEX_PATH
        idmap_path = idmap_path or FAISS_IDMAP_PATH
        faiss.write_index(self.index, str(index_path))
        idmap_path.write_text(json.dumps(self.chunk_ids), encoding="utf-8")

    @classmethod
    def load(
        cls,
        index_path: Path | None = None,
        idmap_path: Path | None = None,
        dimension: int = EMBEDDING_DIMENSION,
    ) -> "VectorStore":
        index_path = index_path or FAISS_INDEX_PATH
        idmap_path = idmap_path or FAISS_IDMAP_PATH
        store = cls(dimension=dimension)
        if not Path(index_path).exists() or not Path(idmap_path).exists():
            return store
        try:
            store.index = faiss.read_index(str(index_path))
            store.chunk_ids = json.loads(Path(idmap_path).read_text(encoding="utf-8"))
        except Exception as exc:
            logger.exception("Failed to load FAISS index; starting empty.")
            raise VectorStoreError("The vector index could not be loaded.") from exc
        return store

    def clear(self) -> None:
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunk_ids = []

    def persist_clear(self) -> None:
        self.clear()
        if FAISS_INDEX_PATH.exists():
            FAISS_INDEX_PATH.unlink()
        if FAISS_IDMAP_PATH.exists():
            FAISS_IDMAP_PATH.unlink()


def hits_to_records(
    hits: list[tuple[int, float]],
    chunks_by_id: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for chunk_id, score in hits:
        chunk = chunks_by_id.get(chunk_id)
        if not chunk:
            continue
        item = dict(chunk)
        item["score"] = score
        records.append(item)
    return records
