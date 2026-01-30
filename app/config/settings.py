from __future__ import annotations

from dataclasses import dataclass
from os import getenv


def getIntEnv(name: str, default: int) -> int:
    raw_value = getenv(name, default)
    try:
        return int(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
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


def getSettings() -> Settings:
    return Settings(
        ollama_base_url=getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_chat_model=getenv("OLLAMA_CHAT_MODEL", ""),
        ollama_embed_model=getenv("OLLAMA_EMBED_MODEL", ""),
        sources_path=getenv("SOURCES_PATH", "app/ingest/sources.yaml"),
        index_dir=getenv("INDEX_DIR", "app/index_store"),
        chunk_size=getIntEnv("CHUNK_SIZE", 1000),
        chunk_overlap=getIntEnv("CHUNK_OVERLAP", 200),
        retriever_top_k=getIntEnv("RETRIEVER_TOP_K", 5),
        request_timeout_seconds=getIntEnv("REQUEST_TIMEOUT_SECONDS", 30),
        max_retries=getIntEnv("MAX_RETRIES", 3),
    )


settings = getSettings()
