# Enterprise Document Intelligence & Knowledge Assistant

A portfolio RAG application that indexes uploaded enterprise documents and answers questions using retrieved passages, with visible source citations.

This is a demonstration system. It is not connected to a real enterprise. Sample documents are original and synthetic. Local storage is for a single-user demo, not production multi-user persistence. Generated answers should still be reviewed before any real-world decision.

## Overview

Teams often store policies in PDFs and Word files that are hard to search. This project turns those files into a small knowledge assistant: extract text, split it into chunks, embed the chunks, retrieve the closest matches to a question, and ask a language model to answer only from that context.

## Problem statement

Keyword search misses paraphrased policy language, and a generic chatbot can invent rules. This application combines semantic retrieval with a grounded generation prompt so answers stay tied to uploaded documents and show where each claim came from.

## Key features

- Upload PDF, DOCX, and TXT files (multiple files at once)
- Page-aware PDF extraction; no fabricated page numbers for DOCX or TXT
- Configurable chunk size and overlap
- Sentence Transformer embeddings (`all-MiniLM-L6-v2`)
- FAISS vector search across one or many documents
- Grounded answers with source citations
- Document library, duplicate detection, and index removal
- Bundled Northline sample policies for an immediate demo
- Retrieval still works if the LLM API key is missing

## Architecture

```
Documents → Extraction → Chunking → Embeddings → FAISS search → Retrieval → Grounded answer
```

- **SQLite** stores document and chunk metadata
- **FAISS** stores vectors on disk (`data/runtime/`)
- **Streamlit** provides the UI
- **Groq** is the single LLM provider, isolated in `src/llm.py`

## Technology stack

- Python 3.11+
- Streamlit
- PyMuPDF (fitz)
- python-docx
- Sentence Transformers
- FAISS
- SQLite
- Pandas
- Groq Chat Completions API

## Folder structure

```
enterprise-document-intelligence/
├── app/app.py
├── src/
│   ├── config.py
│   ├── database.py
│   ├── document_loader.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retrieval.py
│   ├── llm.py
│   ├── rag_pipeline.py
│   └── document_service.py
├── data/sample_documents/
├── scripts/generate_sample_documents.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## How RAG works in this project

1. Files are extracted to text. PDF pages keep their page numbers.
2. Text is split with a paragraph-aware character window (default 900 characters, 150 overlap) so nearby sentences stay together without a complex splitter.
3. Each chunk is embedded with MiniLM and added to a FAISS inner-product index (normalized vectors ≈ cosine similarity).
4. A question is embedded the same way. Top-k chunks above a similarity floor are kept.
5. Those excerpts are sent to Groq with a prompt that forbids invention. If nothing relevant is retrieved, the UI reports that the answer was not found.
6. Citations list document name and page when a page exists.

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python scripts/generate_sample_documents.py
```

The first embedding run downloads `all-MiniLM-L6-v2` from Hugging Face.

## Environment variables / API configuration

Copy `.env.example` to `.env` (never commit `.env`):

```
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Get a key at [Groq Console](https://console.groq.com/). You can also set the same names in `.streamlit/secrets.toml` locally (that file is gitignored).

Without a key, indexing and retrieval still work. Answer generation is skipped with a clear message.

## How to run

From the project root:

```bash
streamlit run app/app.py
```

## How to use

1. Open **Document Library** and click **Load sample documents**, or use **Upload Documents**.
2. Open **Ask Knowledge Assistant**, enter a question, optionally adjust top-k, and click **Ask**.
3. Read the answer, sources, and expandable retrieved passages.
4. Remove a document from the library if you no longer want it in the index. This does not delete files outside the app index.

## Sample questions

- What is the annual leave entitlement and who needs manager approval for extended leave?
- How long is probation at Northline?
- What is the domestic travel per diem?
- Is USB storage allowed on company laptops?
- What is the default hybrid work pattern?
- Where is the Manchester office and is visitor Wi-Fi available?

## Testing

```bash
pytest
```

Core extraction, chunking, metadata, FAISS, and RAG context tests do not need an API key. LLM calls are mocked or skipped when no key is present.

## Limitations

- No OCR for scanned image-only PDFs
- Single-user local files, not a multi-tenant backend
- MiniLM is small and fast, not a domain-specialized embedding model
- Similarity filtering can miss weakly related passages
- LLM answers can still be imperfect even with retrieved context
- Not a production security or records-management system

## Future improvements

- OCR for scanned PDFs
- Persistent user accounts and access control
- Evaluation set for retrieval quality
- Optional re-ranking
- Replace Groq by swapping `src/llm.py`

## Portfolio / demo disclaimer

This repository is a portfolio demonstration. Sample Northline policies are fictional and original. The application is not affiliated with any employer. Do not use it as the system of record for real HR, legal, or security decisions. Runtime indexes and databases under `data/runtime/` are local demo persistence only.

Deployment to hosting platforms is intentionally not included.
