#!/usr/bin/env python3
"""
Update database with blog posts from JSON results file.
Uses MCP Supabase access.
"""

import json
import os
import sys

# Read the results
results_file = os.path.join(os.path.dirname(__file__), 'batch_1_results.json')
with open(results_file, 'r', encoding='utf-8') as f:
    results = json.load(f)

print(f"Found {len(results)} results to update")
print()

# For each result, we'll generate the SQL statement
# But since we're using MCP, we'll just print them for manual execution
# or we can use the execute_sql tool directly

for i, result in enumerate(results, 1):
    if not result.get('success'):
        print(f"[SKIP] {result.get('course_code', 'unknown')} - not successful")
        continue
    
    course_slug = result['course_slug']
    course_code = result['course_code']
    title = result['title']
    content = result['content']
    meta_description = result.get('meta_description', '')
    
    print(f"[{i}/5] Updating {course_code} ({course_slug})")
    print(f"  Title: {title[:60]}...")
    print(f"  Content length: {len(content)} chars")
    print(f"  Word count: {result.get('word_count', 0)}")
    print()

print("\nAll courses processed. SQL statements would be generated here.")
print("Since we're using MCP, we'll update directly via execute_sql tool.")

