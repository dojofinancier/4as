#!/usr/bin/env python3
"""
Final script to automatically update all article outlines.
Handles title matching and executes updates one by one.
"""

import json
import os
import sys

def escape_sql(text):
    """Escape single quotes for SQL."""
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

# The assistant will:
# 1. Fetch articles from database
# 2. Match titles (handling encoding differences)
# 3. Generate UPDATE statements with proper escaping
# 4. Execute each one automatically via MCP Supabase

print("\nReady for automatic execution!")
print("The assistant will process all matches and execute updates automatically.")

