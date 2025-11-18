#!/usr/bin/env python3
"""Generate complete SQL for all 250 articles"""
import csv
import re
import unicodedata
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def generate_slug(title: str) -> str:
    """Generate SEO-friendly slug from title."""
    slug = unicodedata.normalize('NFD', title)
    slug = ''.join(c for c in slug if unicodedata.category(c) != 'Mn')
    slug = re.sub(r'[^a-z0-9]+', '-', slug.lower())
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug[:100]

# Read CSV
csv_path = os.path.join(os.path.dirname(__file__), '..', 'blog', 'articles_250_real_titles.csv')
articles = []

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row['title'].strip()
        category = row['category'].strip()
        if title and category:
            slug = generate_slug(title)
            title_escaped = title.replace("'", "''")
            category_escaped = category.replace("'", "''")
            articles.append((slug, title_escaped, category_escaped))

# Generate SQL in batches of 50
batch_size = 50
for i in range(0, len(articles), batch_size):
    batch = articles[i:i+batch_size]
    values = [f"('{slug}', '{title}', '{category}', 'draft_outline', NOW(), NOW())" 
              for slug, title, category in batch]
    
    sql = f"""
INSERT INTO general_articles (slug, title, category, status, created_at, updated_at)
VALUES {','.join(values)}
ON CONFLICT (slug) 
DO UPDATE SET
    title = EXCLUDED.title,
    category = EXCLUDED.category,
    updated_at = NOW();
"""
    print(f"-- Batch {i//batch_size + 1}: Articles {i+1} to {min(i+batch_size, len(articles))}")
    print(sql)

print(f"\n-- Total articles processed: {len(articles)}")

