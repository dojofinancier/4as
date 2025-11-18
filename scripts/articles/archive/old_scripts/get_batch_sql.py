#!/usr/bin/env python3
"""
Generate a simple SQL chunk that updates a small batch of outlines.
Usage: python get_batch_sql.py <start_index> <batch_size>
"""

import json
import os
import sys
import unicodedata

def normalize_text(text: str) -> str:
    if not text:
        return ""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn").lower().strip()

def build_sql(batch, start):
    payload = [{"title": title, "outline": outline} for title, outline in batch]
    json_str = json.dumps(payload)
    tag = f"batch{start}"
    delimiter = f"${tag}$"
    if delimiter in json_str:
        tag = f"batch{start}_alt"
        delimiter = f"${tag}$"
    json_literal = f"{delimiter}{json_str}{delimiter}"

    sql = f"""WITH src AS (
  SELECT *
  FROM json_populate_recordset(NULL::record, {json_literal})
    AS (title text, outline text)
)
UPDATE general_articles ga
SET draft_outline = src.outline,
    status = 'draft',
    updated_at = NOW()
FROM src
WHERE ga.title = src.title
  AND ga.status = 'draft_outline';"""
    return sql

def main():
    if len(sys.argv) < 3:
        print("Usage: python get_batch_sql.py <start_index> <batch_size>")
        sys.exit(1)

    start = int(sys.argv[1])
    size = int(sys.argv[2])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "extracted_outlines.json")

    with open(json_path, "r", encoding="utf-8") as f:
        outlines = json.load(f)

    items = list(outlines.items())
    batch = items[start:start+size]

    if not batch:
        print("-- EMPTY BATCH --")
        return

    sql = build_sql(batch, start)
    print(sql)

if __name__ == "__main__":
    main()

