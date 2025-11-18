#!/usr/bin/env python3
"""
Script to generate SQL UPDATE statements for all remaining courses.
This will be used to update the database via MCP Supabase.
"""

import json
import os

# Courses already updated
updated = {'fin5521', 'fin5523', 'fin5550', 'fin5570'}

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

print(f"Total courses to update: {len(courses_to_update)}\n")

# Generate SQL for each course - we'll execute these via MCP
for result in courses_to_update:
    course_slug = result['course_slug']
    course_code = result['course_code']
    title = result['title']
    content = result['content']
    meta_description = result.get('meta_description', '')
    
    print(f"Course: {course_code} ({course_slug}) - {result.get('word_count', 0)} words")

