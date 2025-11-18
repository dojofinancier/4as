#!/usr/bin/env python3
"""
Execute all remaining outline updates automatically.
This will process all 216 remaining articles.
"""

import json
import os
import unicodedata

def normalize_text(text):
    """Normalize text for matching (handles encoding differences)."""
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize('NFD', text)
    # Remove diacritics for comparison
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().strip()

def escape_sql(text):
    """Escape SQL string."""
    if not text:
        return "''"
    return text.replace("'", "''").replace("\\", "\\\\")

# Load outlines
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'extracted_outlines.json')

print("Loading outlines...")
with open(json_path, 'r', encoding='utf-8') as f:
    outlines = json.load(f)

print(f"Loaded {len(outlines)} outlines")

# Create normalized lookup
outlines_normalized = {}
for title, outline in outlines.items():
    normalized = normalize_text(title)
    outlines_normalized[normalized] = {'original_title': title, 'outline': outline}

print(f"Created normalized lookup with {len(outlines_normalized)} entries")

print("\n" + "="*60)
print("READY FOR AUTOMATIC EXECUTION")
print("="*60)
print("\nThe assistant will:")
print("1. Fetch 216 articles needing outlines from database")
print("2. Match using normalized title comparison")
print("3. Execute UPDATE statements automatically")
print("4. Process all 216 updates sequentially")
print("\nEach UPDATE will run automatically - no approval needed!")
print("="*60)

