"""Document ingest, demo loading, deletion, and index rebuild."""

from __future__ import annotations

import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Any

from src import database as db
from src.chunking import chunk_document
from src.config import SAMPLE_DOCUMENTS_DIR, SUPPORTED_EXTENSIONS, ensure_runtime_dirs
from src.document_loader import DocumentLoadError, extract_file
from src.embeddings import embed_texts
from src.vector_store import VectorStore

logger = logging.getLogger(__name__)


class DocumentServiceError(Exception):
    pass


class DocumentService:
    def __init__(self, store: VectorStore | None = None) -> None:
        ensure_runtime_dirs()
        db.init_db()
        self.store = store if store is not None else VectorStore.load()
        self._sync_index_if_needed()

    def _chunks_by_id(self) -> dict[int, dict[str, Any]]:
        return {int(c["id"]): c for c in db.list_all_chunks()}

    def chunks_by_id(self) -> dict[int, dict[str, Any]]:
        return self._chunks_by_id()

    def stats(self) -> dict[str, Any]:
        return {
            "documents": db.document_count(),
            "chunks": db.chunk_count(),
            "index_size": self.store.size,
            "index_ready": not self.store.is_empty(),
        }

    def list_documents(self) -> list[dict[str, Any]]:
        return db.list_documents()

    def _hash_bytes(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def ingest_path(self, path: Path | str, display_name: str | None = None) -> dict[str, Any]:
        path = Path(path)
        name = display_name or path.name
        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise DocumentServiceError(
                f"Unsupported file type '{suffix}'. Supported types: PDF, DOCX, TXT."
            )
        data = path.read_bytes()
        return self.ingest_bytes(data, name, suffix)

    def ingest_bytes(self, data: bytes, filename: str, suffix: str | None = None) -> dict[str, Any]:
        suffix = (suffix or Path(filename).suffix).lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise DocumentServiceError(
                f"Unsupported file type '{suffix}'. Supported types: PDF, DOCX, TXT."
            )
        if not data:
            raise DocumentServiceError(f"File '{filename}' is empty.")

        content_hash = self._hash_bytes(data)
        existing = db.find_by_hash(content_hash)
        if existing:
            raise DocumentServiceError(
                f"'{filename}' was not added because the same document is already in the library "
                f"(existing file: {existing['name']})."
            )

        document_id = db.insert_document(filename, suffix.lstrip("."), content_hash, status="processing")
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(data)
                tmp_path = Path(tmp.name)
            extracted = extract_file(tmp_path, display_name=filename)
            chunks = chunk_document(extracted, document_id)
            if not chunks:
                raise DocumentLoadError(f"No text chunks could be created from '{filename}'.")

            texts = [c["text"] for c in chunks]
            embeddings = embed_texts(texts)
            chunk_ids = db.insert_chunks(document_id, chunks)
            self.store.add(embeddings, chunk_ids)
            self.store.save()
            db.update_document(document_id, chunk_count=len(chunks), status="ready", error_message="")
            return {
                "document_id": document_id,
                "name": filename,
                "file_type": suffix.lstrip("."),
                "chunk_count": len(chunks),
                "status": "ready",
            }
        except DocumentLoadError as exc:
            logger.info("Ingest failed for %s: %s", filename, exc)
            db.update_document(document_id, status="failed", error_message=str(exc), chunk_count=0)
            db.delete_document(document_id)
            raise DocumentServiceError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Unexpected ingest failure for %s", filename)
            db.update_document(document_id, status="failed", error_message="Processing failed.", chunk_count=0)
            db.delete_document(document_id)
            raise DocumentServiceError(
                f"Could not process '{filename}'. The file may be invalid or the embedding step failed."
            ) from exc
        finally:
            if tmp_path is not None:
                try:
                    tmp_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def remove_document(self, document_id: int) -> None:
        db.delete_document(document_id)
        self.rebuild_index()

    def rebuild_index(self) -> None:
        chunks = db.list_all_chunks()
        self.store.clear()
        if not chunks:
            self.store.persist_clear()
            return
        texts = [c["text"] for c in chunks]
        ids = [int(c["id"]) for c in chunks]
        embeddings = embed_texts(texts)
        self.store.add(embeddings, ids)
        self.store.save()

    def load_sample_documents(self) -> list[dict[str, Any]]:
        SAMPLE_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(
            p
            for p in SAMPLE_DOCUMENTS_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if not files:
            raise DocumentServiceError(
                "No sample documents were found in data/sample_documents. "
                "Run: python scripts/generate_sample_documents.py"
            )
        results: list[dict[str, Any]] = []
        for path in files:
            try:
                results.append(self.ingest_path(path))
            except DocumentServiceError as exc:
                results.append({"name": path.name, "status": "skipped", "message": str(exc)})
        return results

    def _sync_index_if_needed(self) -> None:
        stored = db.chunk_count()
        if stored == 0:
            if not self.store.is_empty():
                self.store.persist_clear()
            return
        if self.store.size != stored:
            logger.info("Rebuilding vector index to match stored chunks (%s vs %s).", stored, self.store.size)
            self.rebuild_index()
