from __future__ import annotations

from os import getenv
from pathlib import Path
from typing import Any

from bs4 import SoupStrainer
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.documents import Document

SOURCE_WEB = "web"
SOURCE_FILES = "files"



def _load_documents_from_web(url: str) -> list[Document]:
    try:
        user_agent = getenv("USER_AGENT") or "Mozilla/5.0 (compatible; RAG-ChallengeBot/1.0)"
        loader = WebBaseLoader(
            url,
            bs_kwargs={"parse_only": SoupStrainer("main")},
            bs_get_text_kwargs={"separator": " ", "strip": True},
            requests_kwargs={"headers": {"User-Agent": user_agent}, "timeout": 25},
        )
        docs = loader.load()
        for doc in docs:
            doc.page_content = " ".join((doc.page_content or "").split())
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


def _filter_pdf_distractor_pages(docs: list[Document]) -> list[Document]:
    # Prevent retrieval distractors from cover/guide pages in PDFs.
    distractors = (
        "technical test",
        "functionality",
        "final words",
        "this test will help",
        "technologies to be used",
        "deployment",
        "quickstart",
        "langserve",
    )
    filtered: list[Document] = []
    for doc in docs:
        content = doc.page_content.lower()
        if any(phrase in content for phrase in distractors):
            continue
        filtered.append(doc)
    return filtered


def load_documents_from_sources(sources: dict[str, Any]) -> list[Document]:
    documents: list[Document] = []

    web_urls = sources.get(SOURCE_WEB) or []
    for url in web_urls:
        if isinstance(url, str) and url.strip():
            documents.extend(_load_documents_from_web(url))
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
            pdf_docs = _load_documents_from_pdf(path)
            documents.extend(_filter_pdf_distractor_pages(pdf_docs))

    return documents
