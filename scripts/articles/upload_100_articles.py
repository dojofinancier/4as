#!/usr/bin/env python3
"""
Upload 100 articles from CSV to the database.

This script reads articles from 100_articles.csv and creates entries
in the general_articles table with status='draft_outline'.
"""

import os
import sys
import csv
import re
import logging
import time
import unicodedata
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase package not installed. Run: pip install supabase")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upload_articles.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing Supabase credentials in .env file")
    logger.error("Required: NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY)")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_slug(title: str) -> str:
    """Generate SEO-friendly slug from title.
    
    Converts accented characters to their non-accented equivalents:
    - é, è, ê, ë → e
    - à, â, ä → a
    - ù, û, ü → u
    - etc.
    """
    # Normalize to NFD (decomposed form) to separate base characters from diacritics
    slug = unicodedata.normalize('NFD', title)
    
    # Remove combining marks (diacritics) - this converts é to e, à to a, etc.
    slug = ''.join(c for c in slug if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase
    slug = slug.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = re.sub(r'^-+|-+$', '', slug)
    
    # Limit length
    return slug[:100]

def load_csv(csv_path: str) -> List[Dict[str, str]]:
    """Load articles from CSV file."""
    articles = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('title', '').strip()
                category = row.get('category', '').strip()
                
                if title and category:
                    articles.append({
                        'title': title,
                        'category': category
                    })
                else:
                    logger.warning(f"Skipping row with missing title or category: {row}")
        
        logger.info(f"Loaded {len(articles)} articles from CSV")
        return articles
    
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return []

def upload_articles(articles: List[Dict[str, str]]) -> Dict[str, int]:
    """Upload articles to database. Returns stats."""
    stats = {
        'created': 0,
        'updated': 0,
        'errors': 0,
        'skipped': 0
    }
    
    logger.info(f"Starting upload of {len(articles)} articles...")
    
    # Process in batches of 20 for better performance
    batch_size = 20
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(articles) + batch_size - 1) // batch_size
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} articles)...")
        
        for article in batch:
            try:
                slug = generate_slug(article['title'])
                
                # Check if article already exists
                existing = supabase.from_('general_articles').select('id, slug').eq('slug', slug).execute()
                
                if existing.data and len(existing.data) > 0:
                    # Update existing article
                    update_data = {
                        'title': article['title'],
                        'category': article['category'],
                        'status': 'draft_outline',
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    
                    result = supabase.from_('general_articles').update(update_data).eq('slug', slug).execute()
                    
                    if result.data:
                        stats['updated'] += 1
                        logger.debug(f"Updated: {article['title'][:50]}...")
                    else:
                        stats['errors'] += 1
                        logger.error(f"Failed to update: {article['title']}")
                
                else:
                    # Create new article
                    insert_data = {
                        'slug': slug,
                        'title': article['title'],
                        'category': article['category'],
                        'status': 'draft_outline',
                        'published': False,
                        'is_indexable': False,
                        'tags': [],
                        'keywords': [],
                        'internal_links': [],
                        'related_articles': [],
                        'external_links': [],
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    
                    result = supabase.from_('general_articles').insert(insert_data).execute()
                    
                    if result.data:
                        stats['created'] += 1
                        logger.debug(f"Created: {article['title'][:50]}...")
                    else:
                        stats['errors'] += 1
                        logger.error(f"Failed to create: {article['title']}")
            
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error processing article '{article['title']}': {e}")
        
        # Small delay between batches to avoid rate limiting
        if i + batch_size < len(articles):
            time.sleep(0.5)
    
    return stats

def main():
    """Main function."""
    csv_path = os.path.join(os.path.dirname(__file__), '100_articles.csv')
    
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("UPLOADING 100 ARTICLES TO DATABASE")
    logger.info("=" * 60)
    
    # Load articles from CSV
    articles = load_csv(csv_path)
    
    if not articles:
        logger.error("No articles found in CSV file")
        sys.exit(1)
    
    # Upload to database
    stats = upload_articles(articles)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("UPLOAD SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total articles processed: {len(articles)}")
    logger.info(f"Created: {stats['created']}")
    logger.info(f"Updated: {stats['updated']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info(f"Skipped: {stats['skipped']}")
    logger.info("=" * 60)
    
    if stats['errors'] > 0:
        logger.warning(f"Completed with {stats['errors']} errors")
        sys.exit(1)
    else:
        logger.info("Upload completed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()

