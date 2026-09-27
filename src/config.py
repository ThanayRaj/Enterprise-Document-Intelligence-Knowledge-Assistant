"""Application configuration. Secrets come from environment or Streamlit secrets, never from source."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DOCUMENTS_DIR = DATA_DIR / "sample_documents"
RUNTIME_DIR = DATA_DIR / "runtime"
DB_PATH = RUNTIME_DIR / "metadata.db"
FAISS_INDEX_PATH = RUNTIME_DIR / "chunks.index"
FAISS_IDMAP_PATH = RUNTIME_DIR / "chunk_ids.json"
LOG_PATH = RUNTIME_DIR / "app.log"

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# Character-based chunking with overlap. Paragraph-aware split is applied first.
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

DEFAULT_TOP_K = 5
MIN_SIMILARITY = 0.28

GROQ_API_URL_HOST = "api.groq.com"
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


def ensure_runtime_dirs() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


def _secret(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    if value:
        return value.strip()
    try:
        import streamlit as st

        secrets = getattr(st, "secrets", None)
        if secrets is not None and name in secrets:
            return str(secrets[name]).strip()
    except Exception:
        pass
    return default


def get_groq_api_key() -> str:
    return _secret("GROQ_API_KEY", "")


def get_groq_model() -> str:
    return _secret("GROQ_MODEL", DEFAULT_GROQ_MODEL) or DEFAULT_GROQ_MODEL


def llm_is_configured() -> bool:
    return bool(get_groq_api_key())
