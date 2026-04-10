"""

Load PDF, DOCX, or TXT files and return a standardised metadata dict.
"""

from __future__ import annotations

import os
from pathlib import Path


def _load_txt(file_path: Path) -> tuple[str, int]:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    return text, 1                          # TXT files have no real "pages"


def _load_pdf(file_path: Path) -> tuple[str, int]:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is required for PDF support: pip install pypdf")

    reader = PdfReader(str(file_path))
    pages  = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(pages)


def _load_docx(file_path: Path) -> tuple[str, int]:
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required for DOCX support: pip install python-docx")

    doc   = Document(str(file_path))
    text  = "\n".join(para.text for para in doc.paragraphs)
    words = len(text.split())
    estimated_pages = max(1, words // 400)
    return text, estimated_pages


_LOADERS = {
    ".txt":  _load_txt,
    ".pdf":  _load_pdf,
    ".docx": _load_docx,
}


def load_document(file_path: str | Path) -> dict:
    """
    Load a document from disk.

    Returns
    -------
    dict with keys:
        filename   : str
        file_path  : str
        extension  : str
        page_count : int
        raw_text   : str
        char_count : int
        word_count : int
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()
    if ext not in _LOADERS:
        raise ValueError(f"Unsupported file type '{ext}'. Supported: {list(_LOADERS)}")

    raw_text, page_count = _LOADERS[ext](path)

    return {
        "filename":   path.name,
        "file_path":  str(path),
        "extension":  ext,
        "page_count": page_count,
        "raw_text":   raw_text,
        "char_count": len(raw_text),
        "word_count": len(raw_text.split()),
    }


def load_all_from_directory(directory: str | Path, extensions: list[str] | None = None) -> list[dict]:
    """
    Load all supported documents from a directory (non-recursive).

    Parameters
    ----------
    directory  : path to scan
    extensions : optional whitelist, e.g. ['.txt', '.pdf']
    """
    allowed = set(extensions or _LOADERS.keys())
    docs    = []

    for entry in sorted(Path(directory).iterdir()):
        if entry.is_file() and entry.suffix.lower() in allowed:
            try:
                docs.append(load_document(entry))
            except Exception as exc:
                print(f"Skipping {entry.name}: {exc}")

    return docs



if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    results = load_all_from_directory(target)
    for r in results[:3]:
        print(r["filename"], "| words:", r["word_count"], "| pages:", r["page_count"])
    print(f"\nTotal loaded: {len(results)}")