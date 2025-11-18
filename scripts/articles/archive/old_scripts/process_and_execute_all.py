#!/usr/bin/env python3
"""
Process all articles, match with outlines, and prepare UPDATE statements.
The assistant will then execute them automatically.
"""

import json
import os
import unicodedata

def normalize(text):
    """Normalize text for matching."""
    if not text:
        return ""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn').lower().strip()

def escape_sql(text):
    """Escape SQL."""
    return text.replace("'", "''").replace("\\", "\\\\") if text else "''"

# Load outlines
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'extracted_outlines.json')

print("Loading outlines...")
with open(json_path, 'r', encoding='utf-8') as f:
    outlines = json.load(f)

# Create normalized lookup
lookup = {normalize(k): {'title': k, 'outline': v} for k, v in outlines.items()}

print(f"Created lookup with {len(lookup)} normalized entries")

# Articles from database (will be fetched by assistant)
print("\nThe assistant will:")
print("1. Fetch all 216 articles needing outlines")
print("2. Match each article title (normalized) with outlines")
print("3. Generate UPDATE SQL for each match")
print("4. Execute all UPDATEs automatically via MCP")
print("\nReady to process!")

