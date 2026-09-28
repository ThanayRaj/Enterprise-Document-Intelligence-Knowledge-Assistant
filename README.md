# Enterprise Document Intelligence & Knowledge Assistant

An AI-powered Retrieval-Augmented Generation (RAG) system that lets users upload enterprise documents and ask questions using grounded answers with document and page-level source citations.

This is a portfolio demonstration of an enterprise document intelligence workflow. It is not connected to a real enterprise system. Sample documents are fictional and original, and local storage is intended for a single-user demo rather than production use.

## Overview

Teams often store policies and internal documents in PDFs, Word files, and text files that can be difficult to search efficiently.

This project converts those documents into searchable knowledge using semantic retrieval and Retrieval-Augmented Generation (RAG).

```text
PDF / DOCX / TXT
→ Text Extraction
→ Chunking
→ Sentence Transformer Embeddings
→ FAISS Semantic Search
→ Relevant Context
→ Groq LLM
→ Grounded Answer + Source Citations
````

The system demonstrates how enterprise document intelligence and grounded AI assistants can be built using modern NLP and retrieval techniques.

## Problem Statement

Traditional keyword search can miss relevant information when users phrase questions differently from the wording used in documents.

Generic chatbots can also generate unsupported information.

This project combines semantic search with grounded generation so answers are based on retrieved document passages and accompanied by visible source citations.

## Key Features

* Upload PDF, DOCX, and TXT documents
* Process multiple documents
* Page-aware PDF extraction
* Paragraph-aware text chunking
* Configurable chunk size and overlap
* Sentence Transformer embeddings using `all-MiniLM-L6-v2`
* FAISS vector similarity search
* Multi-document retrieval
* Grounded RAG answers
* Document and page-level source citations
* Adjustable Top-K retrieval
* Document library
* Duplicate document detection
* Document removal from the search index
* Bundled synthetic sample documents
* Retrieval works without an LLM API key
* Streamlit-based user interface
* SQLite metadata storage

## Architecture

```text
Documents
↓
Document Extraction
↓
Text Chunking
↓
Sentence Transformer Embeddings
↓
FAISS Vector Index
↓
Semantic Retrieval
↓
Relevant Context
↓
Groq LLM
↓
Grounded Answer
↓
Source Citations
```

## Technology Stack

* Python 3.11+
* Streamlit
* PyMuPDF
* python-docx
* Sentence Transformers
* FAISS
* SQLite
* Pandas
* NumPy
* Groq Chat Completions API
* pytest

## Project Structure

```text
enterprise-document-intelligence/
├── app/
│   └── app.py
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
├── data/
│   └── sample_documents/
├── scripts/
│   └── generate_sample_documents.py
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## How RAG Works

1. A user uploads a PDF, DOCX, or TXT document.
2. The application extracts the document text.
3. PDF content retains page information.
4. The extracted text is divided into overlapping chunks.
5. Each chunk is converted into an embedding using `all-MiniLM-L6-v2`.
6. The embeddings are stored in a FAISS vector index.
7. The user's question is converted into an embedding.
8. FAISS retrieves the most relevant document chunks.
9. Retrieved passages are provided to the language model as context.
10. The model is instructed to answer only from the retrieved context.
11. The application displays the answer along with document and page sources.

If relevant information cannot be retrieved, the system reports that the answer was not found instead of intentionally inventing information.

## Installation

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate the bundled sample documents:

```bash
python scripts/generate_sample_documents.py
```

The first embedding run downloads the `all-MiniLM-L6-v2` model from Hugging Face.

## Environment Configuration

Copy `.env.example` to `.env`:

```text
.env.example → .env
```

Then configure:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Never commit the `.env` file or expose your API key publicly.

Without a Groq API key, document indexing and semantic retrieval still work. LLM answer generation is skipped.

## Running the Application

```bash
streamlit run app/app.py
```

## How to Use

1. Open **Document Library** and load the bundled sample documents or upload your own.
2. Open **Ask Knowledge Assistant** and enter a question.
3. Click **Ask**.
4. Review the generated answer, sources, and retrieved passages.
5. Use the Top-K control to adjust the number of retrieved passages.
6. Remove documents from the library when required.

## Sample Questions

* What is the annual leave entitlement?
* How long is the probation period?
* What is the domestic travel per diem?
* Is USB storage allowed on company laptops?
* What is the default hybrid work pattern?
* Where is the Manchester office?
* Is visitor Wi-Fi available?

## Testing

Run:

```bash
pytest
```

The project includes tests covering document extraction, chunking, metadata, FAISS search, retrieval, and RAG context construction.

LLM-dependent tests are mocked or skipped when an API key is unavailable.

## Limitations

* No OCR for scanned image-only PDFs
* Local single-user persistence
* No multi-tenant authentication or authorization
* Small general-purpose embedding model
* Similarity filtering can miss weakly related passages
* LLM-generated answers can still contain errors
* No production-grade security or records-management system
* No large-scale retrieval evaluation dataset

## Future Improvements

* OCR for scanned documents
* User authentication and role-based access control
* Multi-tenant document storage
* Retrieval evaluation datasets
* Retrieval quality monitoring
* Re-ranking models
* Hybrid keyword + semantic search
* Production database and vector database
* Additional LLM providers
* Enterprise deployment architecture

## Portfolio / Demo Disclaimer

This repository is a portfolio demonstration of an enterprise document intelligence and RAG workflow.

The bundled Northline documents are fictional and original.

The application is not affiliated with any employer or enterprise organization.

The system should not be used as the authoritative source for real HR, legal, security, financial, or operational decisions.

Runtime indexes and databases under `data/runtime/` are intended only for local demonstration purposes.

## License

This project is intended for educational and portfolio demonstration purposes.

```
