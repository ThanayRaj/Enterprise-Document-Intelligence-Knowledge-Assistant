"""Straightforward character chunking with overlap and paragraph-aware splitting."""

from __future__ import annotations

from typing import Any

from src.config import CHUNK_OVERLAP, CHUNK_SIZE
from src.document_loader import ExtractedDocument


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 5)

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    units = paragraphs if paragraphs else [text]

    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for unit in units:
        if len(unit) > chunk_size:
            if current:
                flush()
            chunks.extend(_window(unit, chunk_size, overlap))
            continue
        candidate = f"{current}\n\n{unit}".strip() if current else unit
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            flush()
            current = unit
    flush()
    return chunks


def _window(text: str, chunk_size: int, overlap: int) -> list[str]:
    pieces: list[str] = []
    start = 0
    length = len(text)
    step = max(1, chunk_size - overlap)
    while start < length:
        end = min(start + chunk_size, length)
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= length:
            break
        start += step
    return pieces


def chunk_document(
    extracted: ExtractedDocument,
    document_id: int,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    index = 0
    for section in extracted.sections:
        parts = split_text(section.text, chunk_size=chunk_size, overlap=overlap)
        for part in parts:
            records.append(
                {
                    "document_id": document_id,
                    "document_name": extracted.name,
                    "file_type": extracted.file_type,
                    "page_number": section.page_number,
                    "chunk_index": index,
                    "text": part,
                }
            )
            index += 1
    return records
