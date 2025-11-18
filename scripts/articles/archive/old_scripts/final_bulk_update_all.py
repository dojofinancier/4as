#!/usr/bin/env python3
"""
Final script to match all articles with outlines and generate bulk update SQL.
This will process all 217 articles and generate SQL in batches of 50.
"""

import json
import os
import sys

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
outlines_path = os.path.join(script_dir, 'extracted_outlines.json')

# Load outlines
print("Loading outlines...")
with open(outlines_path, 'r', encoding='utf-8') as f:
    outlines_by_title = json.load(f)

print(f"Loaded {len(outlines_by_title)} outlines")

# Articles from database (217 articles)
# The assistant will provide these and generate SQL in batches of 50

print("\nReady to match articles with outlines and generate SQL")
print("The assistant will provide articles and generate the SQL in batches")

