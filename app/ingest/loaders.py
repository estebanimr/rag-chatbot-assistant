"""Source loaders for offline ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.documents import Document


def _load_web(url: str) -> list[Document]:
    """Load a single web URL, returning any extracted documents."""
    try:
        loader = WebBaseLoader(url)
        return loader.load()
    except Exception as exc:
        print(f"Failed to load URL {url}: {exc}")
        return []


def _load_pdf(path: Path) -> list[Document]:
    """Load a single PDF file from disk."""
    try:
        loader = PyPDFLoader(str(path))
        return loader.load()
    except Exception as exc:
        print(f"Failed to load PDF {path}: {exc}")
        return []


def load_sources(sources: dict[str, Any]) -> list[Document]:
    """Load documents from web URLs and optional file entries."""
    documents: list[Document] = []

    web_urls = sources.get("web") or []
    for url in web_urls:
        if isinstance(url, str) and url.strip():
            documents.extend(_load_web(url))

    file_entries = sources.get("files") or []
    for entry in file_entries:
        if not isinstance(entry, dict):
            continue
        path_value = entry.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            continue
        path = Path(path_value)
        if not path.exists():
            continue
        if path.suffix.lower() == ".pdf":
            documents.extend(_load_pdf(path))

    return documents
