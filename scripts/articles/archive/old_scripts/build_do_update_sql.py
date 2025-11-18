#!/usr/bin/env python3
"""
Generate a single DO block that updates all outlines sequentially.
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "scripts" / "articles" / "extracted_outlines.json"
OUT_DIR = ROOT / "scripts" / "articles" / "seq_updates"


def fix_encoding(text: str) -> str:
    if not text:
        return text
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFD", title)
    ascii_only = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return slug[:120]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        outlines = json.load(f)

    items = []
    seen = set()
    for raw_title, raw_outline in outlines.items():
        title = fix_encoding(raw_title)
        outline = fix_encoding(raw_outline)
        slug = slugify(title)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        items.append({"slug": slug, "outline": outline})

    chunk_size = 5
    for idx in range(0, len(items), chunk_size):
        chunk = items[idx : idx + chunk_size]
        json_payload = json.dumps(chunk, ensure_ascii=False, indent=2)
        sql = (
            "DO $$\n"
            "DECLARE\n"
            "    rec jsonb;\n"
            "BEGIN\n"
            "    FOR rec IN SELECT * FROM jsonb_array_elements($$"
            + json_payload.replace("$$", "$$$$")
            + "$$::jsonb)\n"
            "    LOOP\n"
            "        UPDATE general_articles\n"
            "        SET draft_outline = rec->>'outline',\n"
            "            status = 'draft',\n"
            "            updated_at = NOW()\n"
            "        WHERE slug = rec->>'slug';\n"
            "    END LOOP;\n"
            "END $$;\n"
        )
        out_file = OUT_DIR / f"do_batch_{idx // chunk_size + 1:02d}.sql"
        out_file.write_text(sql, encoding="utf-8")
        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()

