"""Streamlit UI for the Enterprise Document Intelligence & Knowledge Assistant."""

from __future__ import annotations

import html
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.config import (
    SAMPLE_DOCUMENTS_DIR,
    SUPPORTED_EXTENSIONS,
    ensure_runtime_dirs,
    llm_is_configured,
)
from src.document_service import DocumentService, DocumentServiceError
from src.rag_pipeline import run_rag

ensure_runtime_dirs()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

st.set_page_config(
    page_title="Northline Knowledge Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: "Source Sans 3", "IBM Plex Sans", sans-serif;
}

.stApp {
    background: #f4f6f8;
    color: #1c2430;
}

header[data-testid="stHeader"] {
    background: rgba(244, 246, 248, 0.92);
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e4e8ee;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.4rem;
}

.brand-mark {
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #5b6b7c;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.brand-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #152033;
    line-height: 1.25;
    margin-bottom: 0.35rem;
}

.brand-sub {
    font-size: 0.88rem;
    color: #5b6b7c;
    margin-bottom: 1.2rem;
}

.page-kicker {
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3d6b8f;
    font-weight: 600;
}

.page-title {
    font-size: 1.85rem;
    font-weight: 700;
    color: #152033;
    margin: 0.15rem 0 0.4rem 0;
}

.page-lead {
    color: #4d5c6d;
    font-size: 1.02rem;
    max-width: 46rem;
    margin-bottom: 1.4rem;
}

.card {
    background: #ffffff;
    border: 1px solid #e4e8ee;
    border-radius: 14px;
    padding: 1.15rem 1.2rem;
    box-shadow: 0 8px 24px rgba(21, 32, 51, 0.04);
    height: 100%;
}

.metric-label {
    font-size: 0.78rem;
    color: #6b7a8c;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}

.metric-value {
    font-size: 1.7rem;
    font-weight: 700;
    color: #152033;
    margin-top: 0.2rem;
}

.metric-hint {
    font-size: 0.82rem;
    color: #6b7a8c;
    margin-top: 0.15rem;
}

.pill {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #eef4f8;
    color: #2d5a78;
    margin-right: 0.35rem;
    margin-bottom: 0.25rem;
}

.flow {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    align-items: center;
    margin: 0.6rem 0 0.2rem 0;
}

.flow-step {
    background: #f7f9fb;
    border: 1px solid #e4e8ee;
    border-radius: 10px;
    padding: 0.45rem 0.7rem;
    font-size: 0.86rem;
    font-weight: 600;
    color: #243447;
}

.flow-arrow {
    color: #8a97a6;
    font-size: 0.9rem;
}

.answer-box {
    background: #ffffff;
    border: 1px solid #dce6ee;
    border-left: 4px solid #2f6f8f;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    font-size: 1.02rem;
    line-height: 1.55;
    color: #1c2430;
}

.source-card {
    background: #ffffff;
    border: 1px solid #e4e8ee;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
}

.source-name {
    font-weight: 650;
    color: #152033;
}

.source-page {
    color: #5b6b7c;
    font-size: 0.9rem;
    margin-top: 0.15rem;
}

.status-ok { color: #1f7a4d; font-weight: 600; }
.status-bad { color: #a33b3b; font-weight: 600; }
.status-warn { color: #8a5a12; font-weight: 600; }

div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e4e8ee;
    border-radius: 14px;
    padding: 0.8rem 1rem;
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid #2f6f8f;
    background: #2f6f8f;
    color: white;
    font-weight: 600;
}

.stButton > button:hover {
    background: #275c77;
    border-color: #275c77;
}

.footer-note {
    color: #7a8796;
    font-size: 0.8rem;
    margin-top: 2rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_service() -> DocumentService:
    if "doc_service" not in st.session_state:
        st.session_state.doc_service = DocumentService()
    return st.session_state.doc_service


def sidebar() -> str:
    service = get_service()
    stats = service.stats()
    with st.sidebar:
        st.markdown('<div class="brand-mark">Northline Internal</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-title">Document Intelligence</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="brand-sub">Knowledge assistant for uploaded enterprise documents.</div>',
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            ["Overview", "Document Library", "Upload Documents", "Ask Knowledge Assistant", "About"],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("Library snapshot")
        c1, c2 = st.columns(2)
        c1.metric("Documents", stats["documents"])
        c2.metric("Chunks", stats["chunks"])
        st.caption("Index: " + ("ready" if stats["index_ready"] else "empty"))
        st.caption("LLM: " + ("configured" if llm_is_configured() else "not configured"))
    return page


def page_overview() -> None:
    service = get_service()
    stats = service.stats()
    st.markdown('<div class="page-kicker">Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Enterprise document intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-lead">Upload policies and manuals, search them semantically, '
        "and receive answers grounded in retrieved passages with source citations.</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    cards = [
        ("Documents", str(stats["documents"]), "In the current library"),
        ("Chunks", str(stats["chunks"]), "Indexed text passages"),
        ("Vector index", "Ready" if stats["index_ready"] else "Empty", "FAISS similarity search"),
        ("LLM", "Ready" if llm_is_configured() else "Not set", "Groq — optional for Q&A"),
    ]
    for col, (label, value, hint) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-hint">{hint}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns((1.35, 1))
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("How it works")
        st.markdown(
            "The assistant never answers from memory. It extracts text, splits it into overlapping "
            "chunks, embeds those chunks, retrieves the closest matches to your question, and only "
            "then asks the language model to answer from that context."
        )
        steps = [
            "Documents",
            "Extraction",
            "Chunking",
            "Embeddings",
            "Vector search",
            "Retrieval",
            "Grounded answer",
        ]
        flow_html = '<div class="flow">'
        for i, step in enumerate(steps):
            flow_html += f'<div class="flow-step">{step}</div>'
            if i < len(steps) - 1:
                flow_html += '<div class="flow-arrow">→</div>'
        flow_html += "</div>"
        st.markdown(flow_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Supported formats")
        st.markdown(
            '<span class="pill">PDF</span><span class="pill">DOCX</span><span class="pill">TXT</span>',
            unsafe_allow_html=True,
        )
        st.write("Page numbers are kept for PDFs. DOCX and TXT are cited by document name only.")
        st.write("If retrieved context does not contain the answer, the assistant says so.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.info(
        "This is a portfolio demonstration with synthetic Northline company documents. "
        "It is not connected to a real enterprise."
    )


def page_library() -> None:
    service = get_service()
    st.markdown('<div class="page-kicker">Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Document library</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-lead">Review indexed documents, load the bundled demo set, or remove items from the local index.</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Load sample documents", use_container_width=True):
            with st.spinner("Indexing sample documents..."):
                try:
                    results = service.load_sample_documents()
                    st.session_state.doc_service = service
                    ready = [r for r in results if r.get("status") == "ready"]
                    skipped = [r for r in results if r.get("status") == "skipped"]
                    if ready:
                        st.success(f"Indexed {len(ready)} sample document(s).")
                    if skipped:
                        st.warning("Some samples were skipped because they are already in the library.")
                except DocumentServiceError as exc:
                    st.error(str(exc))
    with c2:
        st.caption(f"Sample files folder: `{SAMPLE_DOCUMENTS_DIR}`")

    docs = service.list_documents()
    if not docs:
        st.markdown('<div class="card">No documents yet. Upload files or load the sample set.</div>', unsafe_allow_html=True)
        return

    rows = []
    for d in docs:
        rows.append(
            {
                "ID": d["id"],
                "Document": d["name"],
                "Type": d["file_type"].upper(),
                "Chunks": d["chunk_count"],
                "Status": d["status"],
                "Uploaded (UTC)": d["uploaded_at"][:19].replace("T", " "),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.write("")
    ids = [d["id"] for d in docs]
    labels = {d["id"]: f"{d['name']} ({d['file_type']})" for d in docs}
    selected = st.selectbox("Remove a document from the index", ids, format_func=lambda i: labels[i])
    if st.button("Remove selected document"):
        service.remove_document(int(selected))
        st.session_state.doc_service = service
        st.success("Document removed from the library and vector index.")
        st.rerun()


def page_upload() -> None:
    service = get_service()
    st.markdown('<div class="page-kicker">Ingest</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Upload documents</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-lead">Add PDF, DOCX, or TXT files. They are extracted, chunked, embedded, and added to the index without restarting the app.</div>',
        unsafe_allow_html=True,
    )

    files = st.file_uploader(
        "Select one or more files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    if files:
        preview = pd.DataFrame(
            [{"File": f.name, "Type": Path(f.name).suffix.lower().lstrip("."), "Size (KB)": round(len(f.getvalue()) / 1024, 1)} for f in files]
        )
        st.dataframe(preview, use_container_width=True, hide_index=True)

    if st.button("Process uploads", disabled=not files):
        for uploaded in files:
            suffix = Path(uploaded.name).suffix.lower()
            data = uploaded.getvalue()
            with st.status(f"Processing {uploaded.name}", expanded=True) as status:
                if suffix not in SUPPORTED_EXTENSIONS:
                    st.write("Unsupported type.")
                    status.update(label=f"Failed: {uploaded.name}", state="error")
                    continue
                try:
                    result = service.ingest_bytes(data, uploaded.name, suffix)
                    st.write(f"Status: {result['status']}")
                    st.write(f"Chunks generated: {result['chunk_count']}")
                    status.update(label=f"Indexed {uploaded.name}", state="complete")
                except DocumentServiceError as exc:
                    st.write(str(exc))
                    status.update(label=f"Could not index {uploaded.name}", state="error")
        st.session_state.doc_service = service


def page_ask() -> None:
    service = get_service()
    stats = service.stats()
    st.markdown('<div class="page-kicker">Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Ask the knowledge assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-lead">Questions are answered only from retrieved document passages. Unsupported claims are not invented.</div>',
        unsafe_allow_html=True,
    )

    if stats["chunks"] == 0:
        st.warning("The index is empty. Load sample documents or upload files before asking a question.")

    if not llm_is_configured():
        st.info(
            "GROQ_API_KEY is not set. You can still retrieve sources. "
            "Add the key to `.env` to generate grounded answers."
        )

    question = st.text_area(
        "Question",
        placeholder="What is the annual leave entitlement and who needs manager approval for extended leave?",
        height=110,
    )
    top_k = st.slider("Passages to retrieve (top-k)", min_value=3, max_value=10, value=5)
    ask = st.button("Ask", disabled=not question.strip())

    if ask:
        with st.spinner("Retrieving relevant passages..."):
            result = run_rag(
                question,
                service.store,
                service.chunks_by_id(),
                top_k=top_k,
            )
        st.session_state.last_rag = result

    result = st.session_state.get("last_rag")
    if not result:
        return

    st.markdown("#### Question")
    st.write(result.question)
    st.markdown("#### Answer")
    safe_answer = html.escape(result.answer).replace("\n", "<br>")
    st.markdown(f'<div class="answer-box">{safe_answer}</div>', unsafe_allow_html=True)

    st.markdown("#### Sources")
    if not result.sources:
        st.caption("No supporting sources.")
    else:
        for i, source in enumerate(result.sources, start=1):
            page_html = (
                f'<div class="source-page">Page {source["page_number"]}</div>'
                if source.get("page_number") is not None
                else '<div class="source-page">Page number not available for this file type</div>'
            )
            st.markdown(
                f'<div class="source-card"><div class="source-name">{i}. {source["document_name"]}</div>{page_html}</div>',
                unsafe_allow_html=True,
            )

    with st.expander("Retrieved context"):
        if not result.chunks:
            st.write("No passages met the similarity threshold.")
        for chunk in result.chunks:
            page = f" — page {chunk['page_number']}" if chunk.get("page_number") is not None else ""
            st.markdown(f"**{chunk.get('document_name')}{page}** · score {chunk.get('score', 0):.3f}")
            st.write(chunk.get("text", ""))
            st.divider()


def page_about() -> None:
    st.markdown('<div class="page-kicker">About</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">System information</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="card">'
        "<p>This application is a portfolio RAG demo. Sample policies belong to a fictional company (Northline). "
        "They are original synthetic documents and are not copied from any employer.</p>"
        "<p><strong>Stack:</strong> Python, Streamlit, PyMuPDF, python-docx, Sentence Transformers "
        "(all-MiniLM-L6-v2), FAISS, SQLite, Groq LLM API.</p>"
        "<p>Metadata lives in SQLite. Vectors live in a local FAISS index. "
        "That local persistence is suitable for a single-user demonstration, not production multi-user storage.</p>"
        "<p>Answers are grounded in retrieved context and should still be reviewed before any real-world decision.</p>"
        "</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    page = sidebar()
    if page == "Overview":
        page_overview()
    elif page == "Document Library":
        page_library()
    elif page == "Upload Documents":
        page_upload()
    elif page == "Ask Knowledge Assistant":
        page_ask()
    else:
        page_about()
    st.markdown(
        '<div class="footer-note">Portfolio demonstration · not a production enterprise system · deployment not included</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
