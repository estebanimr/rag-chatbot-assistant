"""Offline ingestion entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from app.config.settings import get_settings
from app.ingest.indexer import build_index
from app.ingest.loaders import load_sources


def _read_sources(path: str) -> dict[str, Any]:
    """Load source configuration from a YAML file."""
    source_path = Path(path)
    try:
        with source_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except OSError as exc:
        raise ValueError(f"Unable to read sources YAML at {source_path}") from exc
    if not isinstance(data, dict):
        raise ValueError("Sources YAML must be a mapping.")
    return data


def main() -> int:
    """Run the offline ingestion pipeline."""
    settings = get_settings()
    sources = _read_sources(settings.sources_path)
    web_count = len(sources.get("web") or [])

    documents = load_sources(sources)
    chunks = build_index(documents, settings)

    print(
        "Web sources: "
        f"{web_count}, documents: {len(documents)}, "
        f"chunks: {chunks}, index_dir: {settings.index_dir}"
    )

    if chunks == 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
