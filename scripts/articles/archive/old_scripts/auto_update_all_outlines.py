#!/usr/bin/env python3
"""
Automatically update all article outlines one by one.
This script will be executed by the assistant to process all updates.
"""

import json
import os

def escape_sql(text):
    """Escape single quotes for SQL."""
    return text.replace("'", "''") if text else "''"

# Load outlines
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'extracted_outlines.json')

with open(json_path, 'r', encoding='utf-8') as f:
    outlines = json.load(f)

print(f"Loaded {len(outlines)} outlines from JSON")

# Articles from database (217 articles - will be fetched by assistant)
# For now, we'll process them as the assistant executes

print("\nReady to process updates!")
print("The assistant will:")
print("1. Fetch articles needing outlines")
print("2. Match with outlines dictionary")
print("3. Execute UPDATE statements automatically")
print("4. Show progress for each update")

