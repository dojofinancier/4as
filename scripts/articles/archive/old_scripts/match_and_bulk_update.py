#!/usr/bin/env python3
"""
Match articles with outlines and generate bulk UPDATE SQL using UPDATE ... FROM VALUES pattern.
This is the efficient way to update many rows at once.
"""

import json
import sys
import os

# Read the extracted outlines JSON
print("Loading outlines from JSON...")
with open('scripts/articles/extracted_outlines.json', 'r', encoding='utf-8') as f:
    outlines_data = json.load(f)

print(f"Loaded {len(outlines_data)} outlines from JSON")

# Read articles from database query result (we'll get this from MCP)
# For now, we'll create a script that generates SQL that can be executed

# The articles we need to update (217 articles from the query)
# We'll match by title

def escape_sql_string(text):
    """Escape single quotes for SQL."""
    if not text:
        return "''"
    return text.replace("'", "''")

def generate_bulk_update_sql(articles, outlines_dict, batch_size=50):
    """
    Generate bulk UPDATE SQL using UPDATE ... FROM VALUES pattern.
    
    Pattern:
    UPDATE general_articles AS ga
    SET draft_outline = v.outline::text,
        status = 'draft',
        updated_at = NOW()
    FROM (VALUES
        ('slug1', 'outline1'),
        ('slug2', 'outline2'),
        ...
    ) AS v(slug, outline)
    WHERE ga.slug = v.slug;
    """
    
    # Match articles with outlines
    matched = []
    unmatched = []
    
    for article in articles:
        title = article['title']
        slug = article['slug']
        
        # Find matching outline by title
        outline = outlines_dict.get(title)
        if outline:
            matched.append({
                'slug': slug,
                'outline': outline
            })
        else:
            unmatched.append(title)
            print(f"WARNING: No outline found for: {title}")
    
    print(f"\nMatched: {len(matched)} articles")
    print(f"Unmatched: {len(unmatched)} articles")
    
    if not matched:
        print("No matches found. Exiting.")
        return None
    
    # Generate SQL in batches
    sql_batches = []
    for i in range(0, len(matched), batch_size):
        batch = matched[i:i+batch_size]
        
        # Build VALUES clause
        values_clauses = []
        for item in batch:
            slug = item['slug']
            outline = escape_sql_string(item['outline'])
            values_clauses.append(f"('{slug}', '{outline}')")
        
        values_sql = ',\n        '.join(values_clauses)
        
        sql = f"""UPDATE general_articles AS ga
SET draft_outline = v.outline::text,
    status = 'draft',
    updated_at = NOW()
FROM (VALUES
        {values_sql}
    ) AS v(slug, outline)
WHERE ga.slug = v.slug;"""
        
        sql_batches.append(sql)
    
    return sql_batches

# Create outlines dictionary keyed by title
outlines_dict = {}
for item in outlines_data:
    title = item.get('title', '')
    outline = item.get('outline', '')
    if title and outline:
        outlines_dict[title] = outline

print(f"Created outlines dictionary with {len(outlines_dict)} entries")

# The articles list will be provided by reading from a file or passed as argument
# For now, we'll generate a template that can be filled in

if __name__ == '__main__':
    print("\nThis script needs the articles list from the database.")
    print("The assistant will call this with the articles data.")
    print(f"Outlines dictionary ready with {len(outlines_dict)} entries.")

