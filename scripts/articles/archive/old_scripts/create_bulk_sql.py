#!/usr/bin/env python3
"""
Create bulk update SQL by matching articles with outlines.
Run this from the scripts/articles directory.
"""

import json
import re
import sys
import os

# Fix path for logging
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load outlines
print("Loading outlines...")
with open('extracted_outlines.json', 'r', encoding='utf-8') as f:
    outlines_by_title = json.load(f)

print(f"Loaded {len(outlines_by_title)} outlines")

# Articles from database (220 articles)
# We'll match by title and build SQL
articles_data = """
[{"slug":"approche-pratique-de-excel","title":"Approche pratique de Excel","category":"Outils & technologie"},{"slug":"approche-pratique-de-la-finance-de-base","title":"Approche pratique de la finance de base","category":"Méthodes d'étude & productivité"},{"slug":"approche-pratique-de-la-memorisation-active","title":"Approche pratique de la mémorisation active","category":"Outils & technologie"},{"slug":"approche-pratique-de-la-methodologie-universitaire","title":"Approche pratique de la méthodologie universitaire","category":"Méthodes d'étude & productivité"},{"slug":"approche-pratique-de-la-microeconomie","title":"Approche pratique de la microéconomie","category":"Outils & technologie"},{"slug":"approche-pratique-de-la-motivation","title":"Approche pratique de la motivation","category":"Outils & technologie"},{"slug":"approche-pratique-de-la-planification-de-session","title":"Approche pratique de la planification de session","category":"Orientation universitaire & carrière"},{"slug":"approche-pratique-de-le-management","title":"Approche pratique de le management","category":"Orientation universitaire & carrière"},{"slug":"approche-pratique-de-les-etudes-de-cas","title":"Approche pratique de les études de cas","category":"Réussite aux examens"},{"slug":"approche-pratique-de-les-examens-difficiles","title":"Approche pratique de les examens difficiles","category":"Vie universitaire & bien-être"}]
"""

# Parse articles (we'll use the full list from the database query)
# For now, let's build the matching logic
articles = json.loads(articles_data)

updates = []
matched = 0
unmatched = []

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
        print(f"WARNING: No outline for: {title}")
        continue
    
    # Escape for SQL
    outline_escaped = outline.replace("'", "''")
    updates.append(f"('{slug}', '{outline_escaped}')")
    matched += 1

print(f"\nMatched: {matched}/{len(articles)}")
if unmatched:
    print(f"Unmatched: {len(unmatched)} articles")

if updates:
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
    
    with open('bulk_outline_update.sql', 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f"\nSQL saved to bulk_outline_update.sql ({len(sql)} chars)")
else:
    print("No updates to generate!")

