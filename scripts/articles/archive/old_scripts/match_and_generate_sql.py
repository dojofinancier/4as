#!/usr/bin/env python3
"""
Match articles with outlines and generate bulk update SQL.
This script will process all articles and generate SQL in batches.
"""

import json
import os

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
outlines_path = os.path.join(script_dir, 'extracted_outlines.json')

# Load outlines
print("Loading outlines...")
with open(outlines_path, 'r', encoding='utf-8') as f:
    outlines_by_title = json.load(f)

print(f"Loaded {len(outlines_by_title)} outlines")

# Articles from database query (220 articles)
# The assistant will provide these and generate SQL
print("\nReady to match articles with outlines")
print("The assistant will provide articles and generate the SQL")

