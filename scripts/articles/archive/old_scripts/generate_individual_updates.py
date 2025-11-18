#!/usr/bin/env python3
"""
Generate individual UPDATE statements for each article.
Each statement will be properly escaped and ready for execution.
"""

import json
import os

def escape_sql_string(text):
    """Escape single quotes for SQL."""
    if not text:
        return "''"
    return text.replace("'", "''")

# Load outlines
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'extracted_outlines.json')

print("Loading outlines...")
with open(json_path, 'r', encoding='utf-8') as f:
    outlines_dict = json.load(f)

print(f"Loaded {len(outlines_dict)} outlines")

# Articles that need updates (from database query)
# The assistant will fetch these dynamically and match them

print("\nScript ready!")
print("The assistant will:")
print("1. Fetch articles from database")
print("2. Match with outlines")
print("3. Generate and execute UPDATE statements one by one")
print("4. All updates will run automatically")

