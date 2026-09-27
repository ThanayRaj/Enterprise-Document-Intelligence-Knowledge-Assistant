"""RAG pipeline: retrieve chunks, build context, generate a grounded answer, attach citations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.config import DEFAULT_TOP_K
from src.llm import LLMError, generate_answer, is_available
from src.retrieval import retrieve
from src.vector_store import VectorStore

NOT_FOUND_MESSAGE = (
    "I couldn't find enough information in the available documents to answer this question."
)

LLM_UNAVAILABLE_MESSAGE = (
    "Retrieved matching passages are shown below, but an answer was not generated "
    "because no LLM API key is configured. Add GROQ_API_KEY to enable grounded answers."
)


@dataclass
class RAGResult:
    question: str
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    chunks: list[dict[str, Any]] = field(default_factory=list)
    llm_used: bool = False
    error: str | None = None


def format_source_label(chunk: dict[str, Any]) -> str:
    name = chunk.get("document_name") or "Unknown document"
    page = chunk.get("page_number")
    if page is None or page == "":
        return str(name)
    return f"{name} — Page {page}"


def unique_sources(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, Any]] = set()
    sources: list[dict[str, Any]] = []
    for chunk in chunks:
        name = chunk.get("document_name") or "Unknown document"
        page = chunk.get("page_number")
        key = (str(name), page)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "document_name": name,
                "page_number": page,
                "label": format_source_label(chunk),
            }
        )
    return sources


def build_context(chunks: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        header = f"[Excerpt {i} | {format_source_label(chunk)}]"
        parts.append(f"{header}\n{chunk.get('text', '').strip()}")
    return "\n\n".join(parts)


def run_rag(
    question: str,
    store: VectorStore,
    chunks_by_id: dict[int, dict[str, Any]],
    top_k: int = DEFAULT_TOP_K,
) -> RAGResult:
    question = (question or "").strip()
    if not question:
        return RAGResult(question=question, answer="Please enter a question.", error="empty_question")

    if store.is_empty():
        return RAGResult(
            question=question,
            answer="No documents are indexed yet. Upload or load sample documents first.",
            error="empty_index",
        )

    chunks = retrieve(question, store, chunks_by_id, top_k=top_k)
    sources = unique_sources(chunks)
    if not chunks:
        return RAGResult(
            question=question,
            answer=NOT_FOUND_MESSAGE,
            sources=[],
            chunks=[],
        )

    context = build_context(chunks)
    if not is_available():
        return RAGResult(
            question=question,
            answer=LLM_UNAVAILABLE_MESSAGE,
            sources=sources,
            chunks=chunks,
            llm_used=False,
            error="llm_not_configured",
        )

    try:
        answer = generate_answer(question, context)
        return RAGResult(
            question=question,
            answer=answer,
            sources=sources,
            chunks=chunks,
            llm_used=True,
        )
    except LLMError as exc:
        return RAGResult(
            question=question,
            answer=str(exc),
            sources=sources,
            chunks=chunks,
            llm_used=False,
            error="llm_failure",
        )
