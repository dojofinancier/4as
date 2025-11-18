#!/usr/bin/env python3
"""
Update all batch 1 courses in database using MCP Supabase.
This script will be executed by the assistant.
"""

import json
import os

# Read results
results_file = os.path.join(os.path.dirname(__file__), 'batch_1_results.json')
with open(results_file, 'r', encoding='utf-8') as f:
    results = json.load(f)

print(f"Preparing to update {len(results)} courses in database...")
print()

# Generate SQL for each course
for i, result in enumerate(results, 1):
    if not result.get('success'):
        print(f"[SKIP] {result.get('course_code', 'unknown')}")
        continue
    
    course_slug = result['course_slug']
    course_code = result['course_code']
    title = result['title']
    content = result['content']
    meta_description = result.get('meta_description', '')
    
    # Escape single quotes for SQL
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
    
    print(f"[{i}/5] {course_code} ({course_slug})")
    print(f"  Title: {title[:60]}...")
    print(f"  Content: {len(content)} chars, {result.get('word_count', 0)} words")
    print()
    print("SQL:")
    print(sql)
    print()
    print("-" * 80)
    print()

print("\nAll SQL statements generated above.")
print("The assistant will execute these via MCP Supabase execute_sql tool.")

