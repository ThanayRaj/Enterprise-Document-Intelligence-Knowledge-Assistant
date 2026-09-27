from __future__ import annotations

from src.rag_pipeline import (
    LLM_UNAVAILABLE_MESSAGE,
    NOT_FOUND_MESSAGE,
    RAGResult,
    build_context,
    format_source_label,
    run_rag,
    unique_sources,
)
from src.vector_store import VectorStore


def test_format_source_label_with_and_without_page():
    assert format_source_label({"document_name": "Employee_Handbook.pdf", "page_number": 14}) == (
        "Employee_Handbook.pdf — Page 14"
    )
    assert format_source_label({"document_name": "Company_Policy.docx", "page_number": None}) == (
        "Company_Policy.docx"
    )


def test_unique_sources_and_context():
    chunks = [
        {"document_name": "Leave_Policy.pdf", "page_number": 3, "text": "Extended leave needs manager approval."},
        {"document_name": "Leave_Policy.pdf", "page_number": 3, "text": "Duplicate source should collapse."},
        {"document_name": "Employee_Handbook.pdf", "page_number": 14, "text": "18 days of annual leave."},
        {"document_name": "Remote_Work_Policy.docx", "page_number": None, "text": "Three office days."},
    ]
    sources = unique_sources(chunks)
    assert len(sources) == 3
    labels = [s["label"] for s in sources]
    assert "Leave_Policy.pdf — Page 3" in labels
    assert "Employee_Handbook.pdf — Page 14" in labels
    assert "Remote_Work_Policy.docx" in labels

    context = build_context(chunks)
    assert "Excerpt 1" in context
    assert "18 days of annual leave" in context
    assert "Remote_Work_Policy.docx" in context


def test_run_rag_empty_index():
    result = run_rag("What is annual leave?", VectorStore(dimension=4), {})
    assert isinstance(result, RAGResult)
    assert result.error == "empty_index"
    assert "No documents" in result.answer


def test_run_rag_without_llm(monkeypatch):
    monkeypatch.setattr("src.rag_pipeline.retrieve", lambda *args, **kwargs: [
        {
            "document_name": "Leave_Policy.pdf",
            "page_number": 3,
            "text": "Extended leave of more than 5 consecutive working days needs manager approval.",
            "score": 0.8,
        }
    ])
    monkeypatch.setattr("src.rag_pipeline.is_available", lambda: False)
    store = VectorStore(dimension=4)
    store.add(__import__("numpy").zeros((1, 4), dtype="float32"), [1])
    result = run_rag("Who approves extended leave?", store, {1: {}})
    assert result.error == "llm_not_configured"
    assert result.answer == LLM_UNAVAILABLE_MESSAGE
    assert result.sources[0]["page_number"] == 3
    assert result.llm_used is False


def test_run_rag_not_found(monkeypatch):
    monkeypatch.setattr("src.rag_pipeline.retrieve", lambda *args, **kwargs: [])
    store = VectorStore(dimension=4)
    store.add(__import__("numpy").zeros((1, 4), dtype="float32"), [1])
    result = run_rag("What is the cafeteria menu?", store, {1: {}})
    assert result.answer == NOT_FOUND_MESSAGE
    assert result.sources == []
