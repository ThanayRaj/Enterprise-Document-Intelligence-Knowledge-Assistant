"""Sentence Transformers embedding service. Real model inference only — no fake vectors."""

from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np

from src.config import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Raised when the embedding model cannot be loaded or used."""


@lru_cache(maxsize=1)
def _load_model():
    try:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model %s", EMBEDDING_MODEL_NAME)
        return SentenceTransformer(EMBEDDING_MODEL_NAME)
    except Exception as exc:
        raise EmbeddingError(
            "The embedding model could not be loaded. Check your internet connection "
            "on first run so the model can download."
        ) from exc


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 384), dtype="float32")
    try:
        model = _load_model()
        vectors = model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.asarray(vectors, dtype="float32")
    except EmbeddingError:
        raise
    except Exception as exc:
        raise EmbeddingError("Failed to generate embeddings for the provided text.") from exc


def embed_query(text: str) -> np.ndarray:
    vectors = embed_texts([text])
    return vectors[0]
