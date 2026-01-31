from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.documents import Document

SOURCE_WEB = "web"
SOURCE_FILES = "files"



def _load_documents_from_web(url: str) -> list[Document]:
    try:
        loader = WebBaseLoader(url, bs_get_text_kwargs={"separator": " ", "strip": True})
        docs = loader.load()
        return docs
    except Exception as exc:
        print(f"Failed to load URL {url}: {exc}")
        return []


def _load_documents_from_pdf(path: Path) -> list[Document]:
    try:
        loader = PyPDFLoader(str(path.resolve()))
        docs = loader.load()
        return docs
    except Exception as exc:
        print(f"Failed to load PDF {path}: {exc}")
        return []


def load_documents_from_sources(sources: dict[str, Any]) -> list[Document]:
    documents: list[Document] = []

    web_urls = sources.get(SOURCE_WEB) or []
    for url in web_urls:
        if isinstance(url, str) and url.strip():
            documents.extend(_load_documents_from_web(url))
    """TODO: Refactor this files entries """
    file_entries = sources.get(SOURCE_FILES) or []
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
            documents.extend(_load_documents_from_pdf(path))

    return documents
