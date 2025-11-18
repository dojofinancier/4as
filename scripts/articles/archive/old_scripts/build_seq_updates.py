#!/usr/bin/env python3
"""
Generate sequential SQL batches to update outlines.
Creates files in scripts/articles/seq_updates/batch_XX.sql
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "scripts" / "articles" / "extracted_outlines.json"
OUT_DIR = ROOT / "scripts" / "articles" / "seq_updates"


def fix_encoding(text: str) -> str:
    """Attempt to fix mojibake (UTF-8 read as Latin1)."""
    if not text:
        return text
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def slugify(title: str) -> str:
    """Generate slug similar to previous logic."""
    normalized = unicodedata.normalize("NFD", title)
    ascii_only = "".join(
        ch for ch in normalized if unicodedata.category(ch) != "Mn"
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return slug[:120]


def escape_literal(text: str) -> str:
    """Escape single quotes for SQL literal."""
    return text.replace("'", "''")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        outlines = json.load(f)

    entries = []
    seen = set()
    for raw_title, raw_outline in outlines.items():
        title = fix_encoding(raw_title)
        outline = fix_encoding(raw_outline)
        slug = slugify(title)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        entries.append((slug, outline))

    batch_size = 5  # smaller batches for sequential execution
    for batch_index in range(0, len(entries), batch_size):
        chunk = entries[batch_index : batch_index + batch_size]
        batch_no = batch_index // batch_size + 1
        lines = ["BEGIN;"]
        for slug, outline in chunk:
            escaped_outline = escape_literal(outline)
            lines.append(
                "UPDATE general_articles SET\n"
                f"    draft_outline = '{escaped_outline}',\n"
                "    status = 'draft',\n"
                "    updated_at = NOW()\n"
                f"WHERE slug = '{slug}';"
            )
        lines.append("COMMIT;")
        batch_file = OUT_DIR / f"batch_{batch_no:03d}.sql"
        batch_file.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
        print(f"Wrote {batch_file}")

    print(f"Total batches written: {len(range(0, len(entries), batch_size))}")


if __name__ == "__main__":
    main()

