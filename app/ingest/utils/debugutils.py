import re
from os import getenv
from langchain_core.documents import Document

def _safeFilenameFromUrl(url: str) -> str:
    """Create a filesystem-safe filename from a URL."""
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_").lower()
    return f"{safe}.txt"


def dumpDocuments(url: str, docs: list[Document]) -> None:
    dump_dir = getenv("INGEST_DUMP_DIR", "").strip()
    if not dump_dir:
        return

    out_dir = Path(dump_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / _safeFilenameFromUrl(url)

    if not docs:
        out_path.write_text(f"URL: {url}\n\nNo documents returned.\n", encoding="utf-8")
        return

    lines: list[str] = []
    lines.append(f"URL: {url}")
    lines.append(f"DOCS: {len(docs)}")
    lines.append("")  # blank line

    # RAW
    lines.append("===== RAW TEXT (ALL DOCS) =====")
    total_raw_chars = 0
    for i, d in enumerate(docs):
        raw = (d.page_content or "")
        total_raw_chars += len(raw)
        meta = d.metadata or {}
        page = meta.get("page", i)
        lines.append(f"\n--- DOC {i} (page={page}) META={meta!r} ---\n")
        lines.append(raw)

    # CLEANED
    lines.append("\n\n===== CLEANED TEXT (ALL DOCS) =====")
    lines.append(f"TOTAL_RAW_CHARS: {total_raw_chars}")
    for i, d in enumerate(docs):
        raw = (d.page_content or "")
        cleaned = " ".join(raw.strip().split())
        meta = d.metadata or {}
        page = meta.get("page", i)
        lines.append(f"\n--- DOC {i} (page={page}) ---\n")
        lines.append(cleaned)

    out_path.write_text("\n".join(lines), encoding="utf-8")