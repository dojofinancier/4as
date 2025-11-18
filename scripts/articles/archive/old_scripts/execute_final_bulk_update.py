#!/usr/bin/env python3
"""
Final script to match articles with outlines and execute bulk update.
This will generate SQL using UPDATE ... FROM VALUES pattern and execute it.
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

# Articles from database (218 articles)
# The assistant will provide these and generate SQL in batches

print("\nReady to match and generate SQL")
print("The assistant will provide articles and generate the SQL")

