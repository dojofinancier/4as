#!/usr/bin/env python3
"""
Script to update all remaining courses by generating SQL that can be executed.
Since content is very long, we'll use a Python script to properly escape and format the SQL.
"""

import json
import os
import sys

# Add parent directory to path to import generate-blog-posts functions
sys.path.insert(0, os.path.dirname(__file__))

# Courses already updated
updated = {'fin5521', 'fin5523', 'fin5550', 'fin5570', 'fin5580'}

# Batch files
batch_files = [
    'batch_2_results.json',
    'batch_3_results.json',
    'batch_4_results.json',
    'batch_5_results.json'
]

all_results = []

# Read all batch results
for batch_file in batch_files:
    file_path = os.path.join(os.path.dirname(__file__), batch_file)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
            all_results.extend(results)

# Filter to only courses that need updating
courses_to_update = [r for r in all_results if r.get('success') and r['course_slug'] not in updated]

print(f"Remaining courses to update: {len(courses_to_update)}")
print(f"Course slugs: {', '.join([r['course_slug'] for r in courses_to_update])}\n")

# For each course, we'll need to execute via MCP Supabase
# This script just lists what needs to be done
for result in courses_to_update:
    print(f"- {result['course_code']} ({result['course_slug']}): {result.get('word_count', 0)} words")

