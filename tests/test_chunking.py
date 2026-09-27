from __future__ import annotations

import pytest

from src.chunking import chunk_document, split_text
from src.document_loader import ExtractedDocument, ExtractedSection


def test_split_text_respects_size_and_overlap():
    text = ("alpha " * 40 + "\n\n" + "bravo " * 40).strip()
    chunks = split_text(text, chunk_size=80, overlap=20)
    assert len(chunks) >= 2
    assert all(len(c) <= 120 for c in chunks)


def test_split_text_empty():
    assert split_text("   ") == []


def test_chunk_document_preserves_page_and_ids():
    extracted = ExtractedDocument(
        name="Leave_Policy.pdf",
        file_type="pdf",
        sections=[
            ExtractedSection(text="Annual leave is 18 days.\n\nManagers approve short leave.", page_number=2),
            ExtractedSection(text="Extended leave needs director approval after ten days.", page_number=3),
        ],
    )
    chunks = chunk_document(extracted, document_id=9, chunk_size=200, overlap=20)
    assert chunks
    assert all(c["document_id"] == 9 for c in chunks)
    assert all(c["document_name"] == "Leave_Policy.pdf" for c in chunks)
    assert all(c["file_type"] == "pdf" for c in chunks)
    pages = {c["page_number"] for c in chunks}
    assert pages == {2, 3}
    assert [c["chunk_index"] for c in chunks] == list(range(len(chunks)))


def test_chunk_document_does_not_invent_pages_for_docx():
    extracted = ExtractedDocument(
        name="Remote_Work_Policy.docx",
        file_type="docx",
        sections=[ExtractedSection(text="Hybrid pattern is three office days.", page_number=None)],
    )
    chunks = chunk_document(extracted, document_id=1, chunk_size=80, overlap=10)
    assert chunks
    assert all(c["page_number"] is None for c in chunks)
