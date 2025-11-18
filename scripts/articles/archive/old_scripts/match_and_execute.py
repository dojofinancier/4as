#!/usr/bin/env python3
"""
Match articles with outlines and prepare for automatic execution.
"""

import json
import os
import unicodedata

def normalize_text(text):
    """Normalize for matching."""
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().strip()

def escape_sql(text):
    """Escape for SQL."""
    return text.replace("'", "''").replace("\\", "\\\\") if text else "''"

# Load outlines
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'extracted_outlines.json')

with open(json_path, 'r', encoding='utf-8') as f:
    outlines = json.load(f)

# Create normalized lookup
lookup = {}
for title, outline in outlines.items():
    key = normalize_text(title)
    lookup[key] = {'title': title, 'outline': outline}

print(f"Created lookup with {len(lookup)} entries")
print("\nReady! The assistant will now:")
print("1. Fetch articles from database")
print("2. Match using normalized titles")
print("3. Execute all UPDATE statements automatically")

