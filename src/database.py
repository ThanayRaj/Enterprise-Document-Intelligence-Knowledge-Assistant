"""SQLite metadata for documents and chunks. Embeddings live in FAISS, not here."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from src.config import DB_PATH, ensure_runtime_dirs


def _connect() -> sqlite3.Connection:
    ensure_runtime_dirs()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                content_hash TEXT NOT NULL UNIQUE,
                uploaded_at TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                error_message TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                page_number INTEGER,
                text TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
            """
        )


def insert_document(
    name: str,
    file_type: str,
    content_hash: str,
    status: str = "processing",
) -> int:
    uploaded_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO documents (name, file_type, content_hash, uploaded_at, chunk_count, status)
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (name, file_type, content_hash, uploaded_at, status),
        )
        return int(cur.lastrowid)


def find_by_hash(content_hash: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE content_hash = ?", (content_hash,)
        ).fetchone()
        return dict(row) if row else None


def update_document(
    document_id: int,
    *,
    chunk_count: int | None = None,
    status: str | None = None,
    error_message: str | None = None,
) -> None:
    fields: list[str] = []
    values: list[Any] = []
    if chunk_count is not None:
        fields.append("chunk_count = ?")
        values.append(chunk_count)
    if status is not None:
        fields.append("status = ?")
        values.append(status)
    if error_message is not None:
        fields.append("error_message = ?")
        values.append(error_message)
    if not fields:
        return
    values.append(document_id)
    with get_connection() as conn:
        conn.execute(f"UPDATE documents SET {', '.join(fields)} WHERE id = ?", values)


def insert_chunks(document_id: int, chunks: list[dict[str, Any]]) -> list[int]:
    ids: list[int] = []
    with get_connection() as conn:
        for chunk in chunks:
            cur = conn.execute(
                """
                INSERT INTO chunks (document_id, chunk_index, page_number, text)
                VALUES (?, ?, ?, ?)
                """,
                (
                    document_id,
                    chunk["chunk_index"],
                    chunk.get("page_number"),
                    chunk["text"],
                ),
            )
            ids.append(int(cur.lastrowid))
    return ids


def list_documents() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM documents ORDER BY uploaded_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_document(document_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        return dict(row) if row else None


def delete_document(document_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))


def list_all_chunks() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.document_id, c.chunk_index, c.page_number, c.text,
                   d.name AS document_name, d.file_type
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.id
            """
        ).fetchall()
        return [dict(r) for r in rows]


def chunk_count() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()
        return int(row["n"]) if row else 0


def document_count() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()
        return int(row["n"]) if row else 0


def db_exists() -> bool:
    return Path(DB_PATH).exists()
