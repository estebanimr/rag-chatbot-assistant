from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from app.config.settings import getSettings
from app.ingest.indexer import buildIndex
from app.ingest.loaders import loadDocumentsFromSources


def readSources(path: str) -> dict[str, Any]:
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
    settings = getSettings()
    sources = readSources(settings.sources_path)
    web_count = len(sources.get("web") or [])

    documents = loadDocumentsFromSources(sources)
    chunks = buildIndex(documents, settings)
    current_path = Path(settings.index_dir) / "current.txt"
    run_dir = current_path.read_text(encoding="utf-8").strip() if current_path.exists() else ""

    print(
        "Web sources: "
        f"{web_count}, documents: {len(documents)}, "
        f"chunks: {chunks}, index_dir: {settings.index_dir}"
    )
    if run_dir:
        print(f"Run directory: {run_dir}")

    if chunks == 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
