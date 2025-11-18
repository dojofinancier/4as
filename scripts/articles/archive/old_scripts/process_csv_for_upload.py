#!/usr/bin/env python3
"""Helper script to process CSV and generate SQL for migration"""
import csv
import re
import unicodedata

def generate_slug(title: str) -> str:
    """Generate SEO-friendly slug from title."""
    # Normalize and remove accents
    slug = unicodedata.normalize('NFD', title)
    slug = ''.join(c for c in slug if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase and replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug.lower())
    slug = re.sub(r'^-+|-+$', '', slug)
    
    # Limit length
    return slug[:100]

# Read CSV and generate SQL
articles = []
with open('scripts/blog/articles_250_real_titles.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row['title'].strip()
        category = row['category'].strip()
        slug = generate_slug(title)
        
        # Escape single quotes in SQL
        title_escaped = title.replace("'", "''")
        category_escaped = category.replace("'", "''")
        
        articles.append({
            'slug': slug,
            'title': title_escaped,
            'category': category_escaped
        })

# Generate SQL VALUES clause
values = []
for art in articles:
    values.append(f"('{art['slug']}', '{art['title']}', '{art['category']}', 'draft_outline', NOW(), NOW())")

sql = f"""
INSERT INTO general_articles (slug, title, category, status, created_at, updated_at)
VALUES {','.join(values)}
ON CONFLICT (slug) 
DO UPDATE SET
    title = EXCLUDED.title,
    category = EXCLUDED.category,
    updated_at = NOW();
"""

print(sql)
print(f"\n-- Total articles: {len(articles)}")

