#!/usr/bin/env python3
"""
Directly generate bulk update SQL by matching articles with outlines.
This script will be run from the workspace root.
"""

import json
import sys

# Load outlines
print("Loading outlines...")
with open('scripts/articles/extracted_outlines.json', 'r', encoding='utf-8') as f:
    outlines_by_title = json.load(f)

print(f"Loaded {len(outlines_by_title)} outlines")

# Articles from database (220 articles)
# These will be matched with outlines
articles = [
    {"slug": "approche-pratique-de-excel", "title": "Approche pratique de Excel"},
    {"slug": "approche-pratique-de-la-finance-de-base", "title": "Approche pratique de la finance de base"},
    # ... (all 220 articles)
]

# For now, let's process a small batch to test
# The assistant will provide the full list and generate complete SQL

print("\nReady to match articles with outlines and generate SQL")
print("The assistant will provide the full article list and execute the matching")

