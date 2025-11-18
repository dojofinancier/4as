#!/usr/bin/env python3
"""
Update database with all generated blog posts from batches 2, 3, 4, and 5.
This script generates SQL that can be executed via MCP Supabase.
"""

import json
import os

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

print(f"Total courses: {len(all_results)}")
print(f"Successful: {sum(1 for r in all_results if r.get('success'))}\n")

# Generate SQL for each successful result
for i, result in enumerate(all_results, 1):
    if not result.get('success'):
        continue
    
    course_slug = result['course_slug']
    course_code = result['course_code']
    title = result['title']
    content = result['content']
    meta_description = result.get('meta_description', '')
    
    # Escape single quotes for SQL (double them)
    title_escaped = title.replace("'", "''")
    content_escaped = content.replace("'", "''")
    meta_escaped = meta_description.replace("'", "''")
    
    sql = f"""UPDATE course_blog_posts
SET 
    title = '{title_escaped}',
    content = '{content_escaped}',
    meta_description = '{meta_escaped}',
    published = true,
    updated_at = NOW()
WHERE course_slug = '{course_slug}';"""
    
    print(f"-- Course {i}: {course_code} ({course_slug})")
    print(sql)
    print()

