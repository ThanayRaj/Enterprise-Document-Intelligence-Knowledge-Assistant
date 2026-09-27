from __future__ import annotations

from pathlib import Path

import pytest

from src import config, database


@pytest.fixture
def tmp_runtime(tmp_path: Path, monkeypatch):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    db_path = runtime / "metadata.db"
    index_path = runtime / "chunks.index"
    idmap_path = runtime / "chunk_ids.json"
    monkeypatch.setattr(config, "RUNTIME_DIR", runtime)
    monkeypatch.setattr(config, "DB_PATH", db_path)
    monkeypatch.setattr(config, "FAISS_INDEX_PATH", index_path)
    monkeypatch.setattr(config, "FAISS_IDMAP_PATH", idmap_path)
    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.init_db()
    return {"runtime": runtime, "db": db_path, "index": index_path, "idmap": idmap_path}
