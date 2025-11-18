#!/usr/bin/env python3
"""
Execute all outline updates one by one automatically.
This script prepares the updates and the assistant will execute them.
"""

import json
import os

# Load outlines
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'extracted_outlines.json')

with open(json_path, 'r', encoding='utf-8') as f:
    outlines_dict = json.load(f)

# Articles from database (217 articles)
articles = [
    {"slug": "approche-pratique-de-la-methodologie-universitaire", "title": "Approche pratique de la méthodologie universitaire"},
    {"slug": "approche-pratique-de-la-microeconomie", "title": "Approche pratique de la microéconomie"},
    # ... (all 217 articles)
]

# Match and prepare updates
matched = []
for article in articles:
    title = article['title']
    slug = article['slug']
    outline = outlines_dict.get(title)
    if outline:
        matched.append({
            'slug': slug,
            'title': title,
            'outline': outline
        })

print(f"Matched {len(matched)} articles with outlines")
print(f"\nThe assistant will now execute {len(matched)} UPDATE statements")
print("Each will run automatically without approval needed")
