from __future__ import annotations

import numpy as np

from src.embeddings import embed_texts


def test_embed_texts_empty_does_not_load_model():
    vectors = embed_texts([])
    assert isinstance(vectors, np.ndarray)
    assert vectors.shape[0] == 0
