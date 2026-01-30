"""Index builder for offline ingestion."""

from __future__ import annotations

import gc
import shutil
import time
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import Settings


def _remove_dir(path: Path) -> None:
    """Remove a directory if it exists, retrying on Windows locks."""
    if not path.exists():
        return
    delay = 0.2
    for attempt in range(5):
        try:
            shutil.rmtree(path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(delay)
            delay *= 2


def _rename_with_retry(source: Path, target: Path) -> None:
    """Rename a path with small retries to avoid Windows file locks."""
    delay = 0.2
    for attempt in range(5):
        try:
            source.rename(target)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(delay)
            delay *= 2


def _atomic_swap(tmp_dir: Path, final_dir: Path) -> None:
    """Atomically promote tmp_dir to final_dir with a safety backup."""
    backup_dir = Path(f"{final_dir}_bak")
    _remove_dir(backup_dir)

    had_final = final_dir.exists()
    if had_final:
        final_dir.rename(backup_dir)

    try:
        _rename_with_retry(tmp_dir, final_dir)
    except Exception:
        if had_final and backup_dir.exists():
            _remove_dir(final_dir)
            backup_dir.rename(final_dir)
        raise
    else:
        _remove_dir(backup_dir)
    finally:
        if tmp_dir.exists():
            _remove_dir(tmp_dir)


def build_index(docs: list[Document], settings: Settings) -> int:
    """Split documents, build embeddings, and persist a Chroma index."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    if not chunks:
        return 0

    tmp_dir = Path(f"{settings.index_dir}_tmp")
    final_dir = Path(settings.index_dir)

    if tmp_dir.exists():
        _remove_dir(tmp_dir)

    embeddings = OllamaEmbeddings(
        base_url=settings.ollama_base_url,
        model=settings.ollama_embed_model,
    )
    vectorstore = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=str(tmp_dir),
    )
    persist = getattr(vectorstore, "persist", None)
    if callable(persist):
        persist()
    del vectorstore
    gc.collect()
    time.sleep(0.2)

    _atomic_swap(tmp_dir, final_dir)
    return len(chunks)
