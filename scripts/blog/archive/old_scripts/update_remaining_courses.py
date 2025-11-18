#!/usr/bin/env python3
"""
Script to update all remaining courses from batches 2, 3, 4, and 5.
This will generate SQL that can be executed via MCP Supabase.
"""

import json
import os

# Courses already updated
updated = {'fin5521', 'fin5523', 'fin5550', 'fin5570'}

# Batch files to process
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

# Generate SQL for each course
for i, result in enumerate(courses_to_update, 1):
    course_slug = result['course_slug']
    course_code = result['course_code']
    title = result['title']
    content = result['content']
    meta_description = result.get('meta_description', '')
    
    # Escape single quotes for SQL (double them)
    title_escaped = title.replace("'", "''")
    content_escaped = content.replace("'", "''")
    meta_escaped = meta_description.replace("'", "''")
    
    print(f"-- Course {i}/{len(courses_to_update)}: {course_code} ({course_slug})")
    print(f"-- Title: {title}")
    print(f"-- Word count: {result.get('word_count', 0)}")
    print()
    print(f"UPDATE course_blog_posts")
    print(f"SET")
    print(f"    title = '{title_escaped}',")
    print(f"    content = '{content_escaped}',")
    print(f"    meta_description = '{meta_escaped}',")
    print(f"    published = true,")
    print(f"    updated_at = NOW()")
    print(f"WHERE course_slug = '{course_slug}';")
    print()
    print("="*80)
    print()
