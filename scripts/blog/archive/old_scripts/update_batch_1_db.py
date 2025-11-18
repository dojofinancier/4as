#!/usr/bin/env python3
"""
Update database with batch 1 generated blog posts.
"""

import json
import os

# Read the results
results_file = os.path.join(os.path.dirname(__file__), 'batch_1_results.json')
with open(results_file, 'r', encoding='utf-8') as f:
    results = json.load(f)

# Generate SQL UPDATE statements
sql_statements = []

for result in results:
    if not result.get('success'):
        print(f"Skipping {result.get('course_code', 'unknown')} - not successful")
        continue
    
    course_slug = result['course_slug']
    title = result['title']
    content = result['content']
    meta_description = result.get('meta_description', '')
    word_count = result.get('word_count', 0)
    
    # Escape single quotes for SQL
    title_escaped = title.replace("'", "''")
    content_escaped = content.replace("'", "''")
    meta_escaped = meta_description.replace("'", "''")
    
    sql = f"""
UPDATE course_blog_posts
SET 
    title = '{title_escaped}',
    content = '{content_escaped}',
    meta_description = '{meta_escaped}',
    published = true,
    updated_at = NOW()
WHERE course_slug = '{course_slug}';
"""
    sql_statements.append(sql.strip())

# Print all SQL statements
print("-- Batch 1: Update blog posts in database")
print("-- Generated blog posts for 5 courses\n")
for i, sql in enumerate(sql_statements, 1):
    print(f"-- Course {i}")
    print(sql)
    print()

