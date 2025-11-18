#!/usr/bin/env python3
"""
Step 4: CSV Upload and Parsing Script

Parse CSV with article titles/ideas and create initial database entries.

CSV Format:
title,category
Comment réussir ses examens,tutoring
Les meilleures techniques de mémorisation,study-tips

Requirements:
- MCP Supabase access (no env vars needed for DB)
- CSV file with title and category columns
"""

import csv
import sys
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('article_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_slug(title: str) -> str:
    """Generate SEO-friendly slug from title."""
    import re
    import unicodedata
    
    # Normalize and remove accents
    slug = unicodedata.normalize('NFD', title)
    slug = ''.join(c for c in slug if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase and replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug.lower())
    slug = re.sub(r'^-+|-+$', '', slug)
    
    # Limit length
    return slug[:100]

def load_csv(csv_path: str) -> List[Dict[str, str]]:
    """Load article titles from CSV file."""
    articles = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'title' not in row or 'category' not in row:
                    logger.warning(f"Skipping row missing required fields: {row}")
                    continue
                
                title = row['title'].strip()
                category = row['category'].strip()
                
                if not title or not category:
                    logger.warning(f"Skipping row with empty title or category: {row}")
                    continue
                
                articles.append({
                    'title': title,
                    'category': category
                })
        
        logger.info(f"Loaded {len(articles)} articles from CSV")
        return articles
    
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return []

def create_article_entries(articles: List[Dict[str, str]]) -> Dict[str, int]:
    """Create database entries for articles. Returns stats."""
    # This function will be called by assistant with MCP Supabase access
    # The assistant will execute SQL INSERT statements
    
    stats = {
        'created': 0,
        'updated': 0,
        'errors': 0
    }
    
    logger.info(f"Preparing to create {len(articles)} article entries")
    
    # Generate SQL statements for each article
    sql_statements = []
    for article in articles:
        slug = generate_slug(article['title'])
        title = article['title'].replace("'", "''")  # Escape single quotes
        category = article['category'].replace("'", "''")
        
        sql = f"""
INSERT INTO general_articles (slug, title, category, status, created_at, updated_at)
VALUES ('{slug}', '{title}', '{category}', 'draft_outline', NOW(), NOW())
ON CONFLICT (slug) 
DO UPDATE SET
    title = EXCLUDED.title,
    category = EXCLUDED.category,
    updated_at = NOW();
"""
        sql_statements.append(sql.strip())
    
    # Save SQL to file for assistant to execute
    with open('scripts/articles/upload_article_titles.sql', 'w', encoding='utf-8') as f:
        f.write("-- SQL statements to create article entries from CSV\n")
        f.write(f"-- Generated: {len(articles)} articles\n\n")
        for sql in sql_statements:
            f.write(sql + "\n\n")
    
    logger.info(f"Generated SQL statements for {len(articles)} articles")
    logger.info("SQL statements saved to scripts/articles/upload_article_titles.sql")
    logger.info("Assistant will execute these statements using MCP Supabase")
    
    return stats

def main():
    """Main function."""
    if len(sys.argv) < 2:
        logger.error("Usage: python upload_article_titles.py <csv_file_path>")
        logger.error("Example: python upload_article_titles.py articles.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    logger.info(f"Loading articles from CSV: {csv_path}")
    
    articles = load_csv(csv_path)
    
    if not articles:
        logger.error("No articles loaded from CSV")
        sys.exit(1)
    
    stats = create_article_entries(articles)
    
    logger.info("=" * 50)
    logger.info("Upload Summary:")
    logger.info(f"  Articles processed: {len(articles)}")
    logger.info(f"  SQL statements generated: {len(articles)}")
    logger.info("=" * 50)
    logger.info("Next step: Assistant will execute SQL statements using MCP Supabase")

if __name__ == '__main__':
    main()

