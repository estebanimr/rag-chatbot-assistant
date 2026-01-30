"""Centralized configuration loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv


def _get_int(name: str, default: int) -> int:
    """Return an int from env var or a safe default when missing/invalid."""
    raw_value = getenv(name, "")
    if raw_value.strip() == "":
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Application settings resolved from environment variables."""

    ollama_base_url: str
    ollama_chat_model: str
    ollama_embed_model: str
    sources_path: str
    index_dir: str
    chunk_size: int
    chunk_overlap: int
    retriever_top_k: int
    request_timeout_seconds: int
    max_retries: int


def get_settings() -> Settings:
    """Build and return a Settings instance from environment variables."""
    return Settings(
        ollama_base_url=getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_chat_model=getenv("OLLAMA_CHAT_MODEL", ""),
        ollama_embed_model=getenv("OLLAMA_EMBED_MODEL", ""),
        sources_path=getenv("SOURCES_PATH", "app/ingest/sources.yaml"),
        index_dir=getenv("INDEX_DIR", "app/index_store"),
        chunk_size=_get_int("CHUNK_SIZE", 1000),
        chunk_overlap=_get_int("CHUNK_OVERLAP", 200),
        retriever_top_k=_get_int("RETRIEVER_TOP_K", 5),
        request_timeout_seconds=_get_int("REQUEST_TIMEOUT_SECONDS", 30),
        max_retries=_get_int("MAX_RETRIES", 3),
    )


settings = get_settings()
