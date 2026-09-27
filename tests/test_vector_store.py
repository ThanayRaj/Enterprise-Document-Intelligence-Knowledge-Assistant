from __future__ import annotations

import numpy as np

from src.vector_store import VectorStore, hits_to_records


def test_empty_index_search():
    store = VectorStore(dimension=4)
    assert store.is_empty()
    assert store.search(np.array([1, 0, 0, 0], dtype="float32"), top_k=3) == []


def test_add_and_retrieve(tmp_path):
    store = VectorStore(dimension=3)
    vectors = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.7, 0.7, 0.0],
        ],
        dtype="float32",
    )
    # already roughly unit-ish; FAISS IP
    store.add(vectors, [10, 20, 30])
    hits = store.search(np.array([1.0, 0.0, 0.0], dtype="float32"), top_k=2)
    assert hits[0][0] == 10
    assert hits[0][1] > hits[1][1]

    index_path = tmp_path / "chunks.index"
    idmap_path = tmp_path / "ids.json"
    store.save(index_path, idmap_path)
    loaded = VectorStore.load(index_path, idmap_path, dimension=3)
    assert loaded.size == 3
    assert loaded.chunk_ids == [10, 20, 30]


def test_hits_to_records_preserve_metadata():
    chunks = {
        10: {
            "id": 10,
            "document_name": "Employee_Handbook.pdf",
            "page_number": 14,
            "text": "18 days",
        }
    }
    records = hits_to_records([(10, 0.91)], chunks)
    assert records[0]["document_name"] == "Employee_Handbook.pdf"
    assert records[0]["page_number"] == 14
    assert records[0]["score"] == 0.91
