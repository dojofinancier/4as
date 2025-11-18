#!/usr/bin/env python3
"""
Update database with all generated blog posts from batches 2, 3, 4, and 5.
Uses MCP Supabase to execute SQL updates.
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
            print(f"Loaded {len(results)} courses from {batch_file}")
    else:
        print(f"Warning: {batch_file} not found, skipping")

print(f"\nTotal courses to update: {len(all_results)}")
print(f"Successful generations: {sum(1 for r in all_results if r.get('success'))}")
print()

# Generate SQL UPDATE statements for each successful result
sql_statements = []

for result in all_results:
    if not result.get('success'):
        print(f"[SKIP] {result.get('course_code', 'unknown')} - generation failed")
        continue
    
    course_slug = result['course_slug']
    course_code = result['course_code']
    title = result['title']
    content = result['content']
    meta_description = result.get('meta_description', '')
    word_count = result.get('word_count', 0)
    
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
    
    sql_statements.append({
        'course_code': course_code,
        'course_slug': course_slug,
        'sql': sql,
        'word_count': word_count
    })
    
    print(f"[READY] {course_code} ({course_slug}) - {word_count} words")

print(f"\n{len(sql_statements)} SQL statements ready to execute")
print("\n" + "="*80)
print("SQL UPDATE STATEMENTS:")
print("="*80 + "\n")

# Print all SQL statements
for i, stmt in enumerate(sql_statements, 1):
    print(f"-- Course {i}/{len(sql_statements)}: {stmt['course_code']} ({stmt['course_slug']})")
    print(f"-- Word count: {stmt['word_count']}")
    print()
    print(stmt['sql'])
    print()
    print("-" * 80)
    print()

print(f"\nTotal: {len(sql_statements)} courses ready to update in database")

