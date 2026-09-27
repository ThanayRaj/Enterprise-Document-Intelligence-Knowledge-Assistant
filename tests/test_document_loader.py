from __future__ import annotations

from pathlib import Path

import fitz
import pytest
from docx import Document

from src.document_loader import DocumentLoadError, extract_file


def test_extract_txt(tmp_path: Path):
    path = tmp_path / "notes.txt"
    path.write_text("Visitor Wi-Fi is disabled at Manchester Studio.", encoding="utf-8")
    extracted = extract_file(path)
    assert extracted.file_type == "txt"
    assert "Manchester Studio" in extracted.full_text
    assert extracted.sections[0].page_number is None


def test_extract_txt_empty(tmp_path: Path):
    path = tmp_path / "empty.txt"
    path.write_text("   \n", encoding="utf-8")
    with pytest.raises(DocumentLoadError, match="empty"):
        extract_file(path)


def test_extract_pdf_pages(tmp_path: Path):
    path = tmp_path / "handbook.pdf"
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Page one mentions 18 days of annual leave.")
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Page two mentions 90-day probation.")
    doc.save(path)
    doc.close()

    extracted = extract_file(path)
    assert extracted.file_type == "pdf"
    assert extracted.sections[0].page_number == 1
    assert extracted.sections[1].page_number == 2
    assert "18 days" in extracted.full_text
    assert "90-day" in extracted.full_text


def test_extract_pdf_no_text(tmp_path: Path):
    path = tmp_path / "blank.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(path)
    doc.close()
    with pytest.raises(DocumentLoadError, match="No extractable text"):
        extract_file(path)


def test_extract_docx(tmp_path: Path):
    path = tmp_path / "remote.docx"
    document = Document()
    document.add_paragraph("Default hybrid pattern is 3 office days and 2 remote days.")
    document.save(path)
    extracted = extract_file(path)
    assert extracted.file_type == "docx"
    assert "3 office days" in extracted.full_text
    assert extracted.sections[0].page_number is None


def test_unsupported_type(tmp_path: Path):
    path = tmp_path / "image.png"
    path.write_bytes(b"not-an-image")
    with pytest.raises(DocumentLoadError, match="Unsupported"):
        extract_file(path)
