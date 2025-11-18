#!/usr/bin/env python3
"""
Automatically execute all outline updates using Supabase Python client.
This script will run all 216 updates automatically without any approval needed.
"""

import json
import os
import sys
import unicodedata
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase package not installed. Run: pip install supabase")
    sys.exit(1)

load_dotenv()

def normalize_text(text):
    """Normalize text for matching."""
    if not text:
        return ""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn').lower().strip()

# Load outlines
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'extracted_outlines.json')

print("Loading outlines...")
with open(json_path, 'r', encoding='utf-8') as f:
    outlines = json.load(f)

# Create normalized lookup
lookup = {}
for title, outline in outlines.items():
    key = normalize_text(title)
    lookup[key] = {'title': title, 'outline': outline}

print(f"Created lookup with {len(lookup)} entries")

# Initialize Supabase client
supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if not supabase_url or not supabase_key:
    print("Error: Supabase credentials not found in .env file")
    print("Need: NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or NEXT_PUBLIC_SUPABASE_ANON_KEY)")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

# Fetch articles needing outlines
print("\nFetching articles from database...")
response = supabase.table('general_articles').select('slug, title').eq('status', 'draft_outline').is_('draft_outline', 'null').execute()

articles = response.data
print(f"Found {len(articles)} articles needing outlines")

# Match and update
matched = 0
updated = 0
errors = 0

print("\n" + "="*60)
print("STARTING AUTOMATIC UPDATES")
print("="*60)

for i, article in enumerate(articles, 1):
    slug = article['slug']
    title = article['title']
    
    # Find matching outline
    normalized_title = normalize_text(title)
    match = lookup.get(normalized_title)
    
    if not match:
        print(f"[{i}/{len(articles)}] SKIP: No outline found for '{title}'")
        continue
    
    matched += 1
    outline = match['outline']
    
    # Update article
    try:
        result = supabase.table('general_articles').update({
            'draft_outline': outline,
            'status': 'draft',
            'updated_at': 'now()'
        }).eq('slug', slug).execute()
        
        updated += 1
        print(f"[{i}/{len(articles)}] ✓ Updated: {title[:50]}...")
        
    except Exception as e:
        errors += 1
        print(f"[{i}/{len(articles)}] ✗ Error updating {slug}: {e}")

print("\n" + "="*60)
print("UPDATE COMPLETE")
print("="*60)
print(f"Total articles: {len(articles)}")
print(f"Matched: {matched}")
print(f"Updated: {updated}")
print(f"Errors: {errors}")
print("="*60)

