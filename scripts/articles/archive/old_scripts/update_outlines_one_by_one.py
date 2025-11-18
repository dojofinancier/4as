#!/usr/bin/env python3
"""
Update article outlines one by one sequentially.
This script will automatically execute all updates without requiring approval.
"""

import json
import os
import sys

# Load outlines from JSON
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'extracted_outlines.json')

print("Loading outlines from JSON...")
with open(json_path, 'r', encoding='utf-8') as f:
    outlines_dict = json.load(f)

print(f"Loaded {len(outlines_dict)} outlines")

# Get articles that need outlines from database
# We'll fetch this via MCP, but for now we have the list from earlier
# The assistant will fetch this dynamically

print("\n" + "="*60)
print("OUTLINE UPDATE PROCESS")
print("="*60)
print("\nThis script will:")
print("1. Fetch articles needing outlines from database")
print("2. Match them with outlines from JSON")
print("3. Update each article one by one automatically")
print("4. Show progress for each update")
print("\nThe assistant will execute this via MCP Supabase")
print("Each UPDATE will run automatically without approval needed")
print("="*60)

