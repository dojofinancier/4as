#!/usr/bin/env python3
"""
Generate and execute bulk update SQL for article outlines.
This script matches articles with outlines and creates a single efficient SQL statement.
"""

import json
import sys
import os

# Load outlines
print("Loading extracted outlines...")
with open('scripts/articles/extracted_outlines.json', 'r', encoding='utf-8') as f:
    outlines_by_title = json.load(f)

print(f"Loaded {len(outlines_by_title)} outlines")

# Articles from database (220 articles with status='draft_outline')
# These were fetched earlier via MCP Supabase
articles = [
    {"slug": "approche-pratique-de-excel", "title": "Approche pratique de Excel", "category": "Outils & technologie"},
    {"slug": "approche-pratique-de-la-finance-de-base", "title": "Approche pratique de la finance de base", "category": "Méthodes d'étude & productivité"},
    {"slug": "approche-pratique-de-la-memorisation-active", "title": "Approche pratique de la mémorisation active", "category": "Outils & technologie"},
    {"slug": "approche-pratique-de-la-methodologie-universitaire", "title": "Approche pratique de la méthodologie universitaire", "category": "Méthodes d'étude & productivité"},
    {"slug": "approche-pratique-de-la-microeconomie", "title": "Approche pratique de la microéconomie", "category": "Outils & technologie"},
    {"slug": "approche-pratique-de-la-motivation", "title": "Approche pratique de la motivation", "category": "Outils & technologie"},
    {"slug": "approche-pratique-de-la-planification-de-session", "title": "Approche pratique de la planification de session", "category": "Orientation universitaire & carrière"},
    {"slug": "approche-pratique-de-le-management", "title": "Approche pratique de le management", "category": "Orientation universitaire & carrière"},
    {"slug": "approche-pratique-de-les-etudes-de-cas", "title": "Approche pratique de les études de cas", "category": "Réussite aux examens"},
    {"slug": "approche-pratique-de-les-examens-difficiles", "title": "Approche pratique de les examens difficiles", "category": "Vie universitaire & bien-être"},
    # ... (all 220 articles will be included)
]

# For now, we'll process in batches to avoid SQL size limits
# Let's match and build SQL
updates = []
matched = 0
unmatched = []

print("\nMatching articles with outlines...")
for article in articles:
    title = article['title']
    slug = article['slug']
    outline = outlines_by_title.get(title)
    
    if not outline:
        # Try partial match
        for outline_title, outline_content in outlines_by_title.items():
            if title.lower() in outline_title.lower() or outline_title.lower() in title.lower():
                outline = outline_content
                print(f"Matched '{title}' with '{outline_title}'")
                break
    
    if not outline:
        unmatched.append(title)
        continue
    
    # Escape for SQL
    outline_escaped = outline.replace("'", "''")
    updates.append(f"('{slug}', '{outline_escaped}')")
    matched += 1

print(f"\nMatched: {matched}/{len(articles)} articles")
if unmatched:
    print(f"Unmatched: {len(unmatched)} articles")
    print("First few unmatched:", unmatched[:5])

if updates:
    # Build SQL using UPDATE ... FROM VALUES (PostgreSQL efficient bulk update)
    sql = f"""
-- Bulk update article outlines
-- Updating {len(updates)} articles
UPDATE general_articles AS ga
SET 
    draft_outline = v.outline::text,
    status = 'draft',
    updated_at = NOW()
FROM (VALUES
    {',\n    '.join(updates)}
) AS v(slug, outline)
WHERE ga.slug = v.slug;
"""
    
    # Save to file
    with open('scripts/articles/bulk_outline_update_final.sql', 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f"\nSQL generated: {len(sql)} characters")
    print(f"SQL saved to: scripts/articles/bulk_outline_update_final.sql")
    print(f"\nReady to execute via MCP Supabase")
else:
    print("No updates to generate!")

