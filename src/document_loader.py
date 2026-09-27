"""Extract text from PDF, DOCX, and TXT files without fabricating page numbers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz
from docx import Document as DocxDocument


class DocumentLoadError(Exception):
    """Raised when a file cannot be read or contains no extractable text."""


@dataclass
class ExtractedSection:
    text: str
    page_number: int | None


@dataclass
class ExtractedDocument:
    name: str
    file_type: str
    sections: list[ExtractedSection]

    @property
    def full_text(self) -> str:
        return "\n\n".join(s.text for s in self.sections if s.text.strip())


def _suffix(path: Path) -> str:
    return path.suffix.lower()


def extract_file(path: Path | str, display_name: str | None = None) -> ExtractedDocument:
    path = Path(path)
    name = display_name or path.name
    suffix = _suffix(path)

    if suffix == ".pdf":
        return _extract_pdf(path, name)
    if suffix == ".docx":
        return _extract_docx(path, name)
    if suffix == ".txt":
        return _extract_txt(path, name)
    raise DocumentLoadError(
        f"Unsupported file type '{suffix}'. Please upload PDF, DOCX, or TXT."
    )


def _extract_pdf(path: Path, name: str) -> ExtractedDocument:
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise DocumentLoadError(
            f"Could not open PDF '{name}'. The file may be corrupted or password-protected."
        ) from exc

    sections: list[ExtractedSection] = []
    try:
        if doc.page_count == 0:
            raise DocumentLoadError(f"PDF '{name}' has no pages.")
        for index, page in enumerate(doc, start=1):
            text = (page.get_text("text") or "").strip()
            if text:
                sections.append(ExtractedSection(text=text, page_number=index))
    finally:
        doc.close()

    if not sections:
        raise DocumentLoadError(
            f"No extractable text was found in '{name}'. Scanned images without OCR are not supported."
        )
    return ExtractedDocument(name=name, file_type="pdf", sections=sections)


def _extract_docx(path: Path, name: str) -> ExtractedDocument:
    try:
        document = DocxDocument(str(path))
    except Exception as exc:
        raise DocumentLoadError(
            f"Could not open DOCX '{name}'. The file may be corrupted or is not a valid Word document."
        ) from exc

    paragraphs = [p.text.strip() for p in document.paragraphs if p.text and p.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text and cell.text.strip()]
            if cells:
                paragraphs.append(" | ".join(cells))

    text = "\n\n".join(paragraphs).strip()
    if not text:
        raise DocumentLoadError(f"No extractable text was found in '{name}'.")
    return ExtractedDocument(
        name=name,
        file_type="docx",
        sections=[ExtractedSection(text=text, page_number=None)],
    )


def _extract_txt(path: Path, name: str) -> ExtractedDocument:
    try:
        raw = path.read_bytes()
    except Exception as exc:
        raise DocumentLoadError(f"Could not read text file '{name}'.") from exc

    if not raw.strip():
        raise DocumentLoadError(f"File '{name}' is empty.")

    text = None
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise DocumentLoadError(f"Could not decode text file '{name}'.")

    text = text.strip()
    if not text:
        raise DocumentLoadError(f"File '{name}' is empty.")
    return ExtractedDocument(
        name=name,
        file_type="txt",
        sections=[ExtractedSection(text=text, page_number=None)],
    )
