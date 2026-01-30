from __future__ import annotations

import gc
import time
from datetime import datetime
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import Settings


def timeStamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def writePointer(index_dir: Path, run_dir: Path) -> None:
    pointer_path = index_dir / "current.txt"
    pointer_path.write_text(str(run_dir.resolve()), encoding="utf-8")


def normalizeDocuments(docs: list[Document]) -> list[Document]:
    """Normalize whitespace in document content before chunking."""
    normalized: list[Document] = []
    for doc in docs:
        new_text = " ".join((doc.page_content or "").split())
        normalized.append(Document(page_content=new_text, metadata=doc.metadata))
    return normalized


def buildIndex(docs: list[Document], settings: Settings) -> int:
    docs = normalizeDocuments(docs)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    if not chunks:
        return 0

    index_dir = Path(settings.index_dir)
    runs_dir = index_dir / "runs"
    run_dir = runs_dir / timeStamp()
    run_dir.mkdir(parents=True, exist_ok=True)

    embeddings = OllamaEmbeddings(
        base_url=settings.ollama_base_url,
        model=settings.ollama_embed_model,
    )
    vectorstore = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=str(run_dir),
    )
    persist = getattr(vectorstore, "persist", None)
    if callable(persist):
        persist()
    del vectorstore
    gc.collect()
    time.sleep(0.2)

    writePointer(index_dir, run_dir)
    return len(chunks)
