#!/usr/bin/env python3
"""
Execute database updates for batch 1 courses.
Reads JSON and executes SQL via print statements that can be copied to MCP.
"""

import json
import os

# Read results
results_file = os.path.join(os.path.dirname(__file__), 'batch_1_results.json')
with open(results_file, 'r', encoding='utf-8') as f:
    results = json.load(f)

# Filter to only the courses that need updating (skip aot3220 which is already done)
courses_to_update = [r for r in results if r['course_slug'] != 'aot3220']

print(f"# Updating {len(courses_to_update)} courses in database\n")

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
    
    sql = f"""UPDATE course_blog_posts
SET 
    title = '{title_escaped}',
    content = '{content_escaped}',
    meta_description = '{meta_escaped}',
    published = true,
    updated_at = NOW()
WHERE course_slug = '{course_slug}';"""
    
    print(f"# Course {i}/{len(courses_to_update)}: {course_code} ({course_slug})")
    print(f"# Title: {title}")
    print(f"# Content: {len(content)} chars, {result.get('word_count', 0)} words")
    print()
    print(sql)
    print()
    print("#" + "="*80)
    print()

