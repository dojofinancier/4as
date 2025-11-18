#!/usr/bin/env python3
"""
Generate complete bulk update SQL by matching all articles with outlines.
This script will process all 220 articles in batches of 50.
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

# The assistant will:
# 1. Fetch all 220 articles from database
# 2. Match them with outlines_by_title by title
# 3. Generate SQL in batches of 50
# 4. Execute each batch via MCP Supabase

print("\nReady to generate bulk update SQL")
print("The assistant will provide articles and generate the SQL in batches")

