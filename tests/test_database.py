from __future__ import annotations

from src import database as db


def test_document_and_chunk_storage(tmp_runtime):
    db.init_db()
    doc_id = db.insert_document("Leave_Policy.pdf", "pdf", "abc123", status="processing")
    db.insert_chunks(
        doc_id,
        [
            {"chunk_index": 0, "page_number": 1, "text": "Eighteen days of annual leave."},
            {"chunk_index": 1, "page_number": None, "text": "No fabricated page."},
        ],
    )
    db.update_document(doc_id, chunk_count=2, status="ready", error_message="")

    docs = db.list_documents()
    assert len(docs) == 1
    assert docs[0]["name"] == "Leave_Policy.pdf"
    assert docs[0]["chunk_count"] == 2
    assert docs[0]["status"] == "ready"

    chunks = db.list_all_chunks()
    assert len(chunks) == 2
    assert chunks[0]["document_name"] == "Leave_Policy.pdf"
    assert chunks[0]["page_number"] == 1
    assert chunks[1]["page_number"] is None

    assert db.find_by_hash("abc123")["id"] == doc_id
    db.delete_document(doc_id)
    assert db.document_count() == 0
    assert db.chunk_count() == 0
