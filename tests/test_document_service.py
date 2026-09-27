from __future__ import annotations

from pathlib import Path

import fitz
import numpy as np
import pytest

from src.document_service import DocumentService, DocumentServiceError
from src.retrieval import retrieve
from src.vector_store import VectorStore


def _tiny_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


class FakeEmbedder:
    """Deterministic stand-in so tests do not require the MiniLM download."""

    def __init__(self) -> None:
        self.vocab = ["leave", "travel", "security", "office", "password", "approval"]

    def encode(self, texts: list[str]) -> np.ndarray:
        rows = []
        for text in texts:
            lowered = text.lower()
            vec = np.array([lowered.count(token) + 0.1 for token in self.vocab], dtype="float32")
            vec = vec / (np.linalg.norm(vec) + 1e-8)
            rows.append(vec)
        return np.vstack(rows)


@pytest.fixture
def fake_embeddings(monkeypatch):
    embedder = FakeEmbedder()

    def embed_texts(texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 6), dtype="float32")
        return embedder.encode(texts)

    def embed_query(text: str) -> np.ndarray:
        return embed_texts([text])[0]

    monkeypatch.setattr("src.document_service.embed_texts", embed_texts)
    monkeypatch.setattr("src.retrieval.embed_query", embed_query)
    monkeypatch.setattr("src.embeddings.embed_texts", embed_texts)
    monkeypatch.setattr("src.embeddings.embed_query", embed_query)
    return embedder


def test_ingest_retrieve_and_remove(tmp_runtime, fake_embeddings, tmp_path: Path, monkeypatch):
    monkeypatch.setattr("src.vector_store.FAISS_INDEX_PATH", tmp_runtime["index"])
    monkeypatch.setattr("src.vector_store.FAISS_IDMAP_PATH", tmp_runtime["idmap"])

    store = VectorStore(dimension=6)
    service = DocumentService(store=store)

    pdf_a = tmp_path / "Leave_Policy.pdf"
    pdf_b = tmp_path / "Travel_Policy.pdf"
    _tiny_pdf(pdf_a, "Employees receive 18 days of annual leave. Extended leave needs manager approval.")
    _tiny_pdf(pdf_b, "Domestic travel needs manager approval. International travel needs director approval.")

    result_a = service.ingest_path(pdf_a)
    result_b = service.ingest_path(pdf_b)
    assert result_a["chunk_count"] >= 1
    assert result_b["status"] == "ready"
    assert service.stats()["documents"] == 2

    with pytest.raises(DocumentServiceError, match="already"):
        service.ingest_path(pdf_a)

    hits = retrieve(
        "How much annual leave and who approves extended leave?",
        service.store,
        service.chunks_by_id(),
        top_k=5,
        min_similarity=0.1,
    )
    names = {h["document_name"] for h in hits}
    assert "Leave_Policy.pdf" in names
    assert all("page_number" in h for h in hits)

    service.remove_document(result_a["document_id"])
    remaining = {d["name"] for d in service.list_documents()}
    assert remaining == {"Travel_Policy.pdf"}
    assert service.store.size == service.stats()["chunks"]


def test_unsupported_and_empty_bytes(tmp_runtime, fake_embeddings, monkeypatch):
    monkeypatch.setattr("src.vector_store.FAISS_INDEX_PATH", tmp_runtime["index"])
    monkeypatch.setattr("src.vector_store.FAISS_IDMAP_PATH", tmp_runtime["idmap"])
    service = DocumentService(store=VectorStore(dimension=6))
    with pytest.raises(DocumentServiceError, match="Unsupported"):
        service.ingest_bytes(b"data", "photo.png", ".png")
    with pytest.raises(DocumentServiceError, match="empty"):
        service.ingest_bytes(b"", "blank.txt", ".txt")
