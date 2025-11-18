#!/usr/bin/env python3
"""
Extract articles from the database output file and create a complete processing script.
"""

import json
import re

# Read the file
with open(r'c:\Users\User\.cursor\projects\c-Users-User-Desktop-4AS-HOME-code-workspace\agent-tools\e0d4d87a-e69b-48f2-b4fd-c71a0314c3c4.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON array from the content
# The JSON is embedded in the text, find it
match = re.search(r'\[.*\]', content, re.DOTALL)
if match:
    json_str = match.group(0)
    articles = json.loads(json_str)
    print(f"Found {len(articles)} articles")
    
    # Save as JSON file
    with open('scripts/articles/all_remaining_articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to scripts/articles/all_remaining_articles.json")
    print(f"First article: {articles[0]['title']}")
else:
    print("Could not find JSON array in file")

