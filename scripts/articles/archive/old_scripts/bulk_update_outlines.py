#!/usr/bin/env python3
"""
Efficient bulk update of article outlines using database slugs and matching by title.
This script:
1. Fetches articles needing outlines from database (with correct slugs)
2. Reads generated outline SQL files
3. Matches by title to get the correct outline
4. Builds a single efficient SQL statement for bulk update
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/articles/bulk_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def read_all_outline_sql_files() -> Dict[str, str]:
    """Read all batch outline SQL files and extract outlines by matching title in content."""
    # We'll match by title since slugs have encoding issues
    # The outline content contains the title, so we can extract it
    outlines_by_title = {}
    scripts_dir = Path('scripts/articles')
    
    # Find all batch_X_outlines.sql files
    batch_files = sorted(scripts_dir.glob('batch_*_outlines.sql'))
    
    logger.info(f"Found {len(batch_files)} batch SQL files")
    
    for batch_file in batch_files:
        logger.info(f"Reading {batch_file.name}")
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove markdown code blocks if present
            content = re.sub(r'```markdown\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            
            # Split into individual UPDATE statements
            statements = re.split(r';\s*(?=UPDATE)', content, flags=re.IGNORECASE | re.DOTALL)
            
            for stmt in statements:
                stmt = stmt.strip()
                if not stmt or not stmt.startswith('UPDATE'):
                    continue
                
                # Extract outline content - everything between draft_outline = ' and ', status = 'draft'
                # The pattern is: draft_outline = '...', status = 'draft', updated_at = NOW() WHERE slug = '...'
                outline_match = re.search(r"draft_outline\s*=\s*'(.*?)'\s*,\s*status", stmt, re.DOTALL)
                if not outline_match:
                    continue
                
                outline = outline_match.group(1)
                # Unescape SQL quotes: '' -> '
                outline = outline.replace("''", "'")
                
                # Extract title from outline (first line after # or ##)
                title_match = re.search(r'^#+\s*(.+?)$', outline, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                    outlines_by_title[title] = outline
                    logger.debug(f"Extracted outline for title: {title[:50]}...")
        
        except Exception as e:
            logger.error(f"Error reading {batch_file}: {e}")
            continue
    
    logger.info(f"Extracted {len(outlines_by_title)} outlines from SQL files")
    return outlines_by_title

def build_bulk_update_sql(articles: List[Dict], outlines_by_title: Dict[str, str]) -> str:
    """Build a single SQL statement to update all articles efficiently."""
    
    # Use PostgreSQL's UPDATE ... FROM VALUES pattern for bulk update
    # Match by title since slugs in SQL files have encoding issues
    
    updates = []
    matched = 0
    unmatched = []
    
    for article in articles:
        title = article['title']
        slug = article['slug']
        outline = outlines_by_title.get(title)
        
        if not outline:
            # Try to find by partial match (in case of slight differences)
            for outline_title, outline_content in outlines_by_title.items():
                if title.lower() in outline_title.lower() or outline_title.lower() in title.lower():
                    outline = outline_content
                    logger.info(f"Matched '{title}' with '{outline_title}'")
                    break
        
        if not outline:
            unmatched.append(title)
            logger.warning(f"No outline found for title: {title} (slug: {slug})")
            continue
        
        # Escape single quotes for SQL
        outline_escaped = outline.replace("'", "''")
        
        # Build VALUES entry
        updates.append(f"('{slug}', '{outline_escaped}')")
        matched += 1
    
    logger.info(f"Matched {matched}/{len(articles)} articles")
    if unmatched:
        logger.warning(f"Unmatched titles: {unmatched[:10]}...")
    
    if not updates:
        logger.error("No updates to apply")
        return None
    
    # Build the SQL using UPDATE ... FROM VALUES
    # PostgreSQL can handle large VALUES lists efficiently
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
    
    return sql.strip()

def main():
    """Main function to orchestrate bulk update."""
    logger.info("="*60)
    logger.info("Bulk Outline Update Script")
    logger.info("="*60)
    
    # Step 1: Read all outline SQL files
    logger.info("\nStep 1: Reading outline SQL files...")
    outlines_by_title = read_all_outline_sql_files()
    
    if not outlines_by_title:
        logger.error("No outlines found in SQL files!")
        return
    
    logger.info(f"✓ Extracted {len(outlines_by_title)} outlines")
    
    # Step 2: Build bulk update SQL
    logger.info("\nStep 2: Building bulk update SQL...")
    logger.info("Note: Articles will be fetched from database via MCP Supabase")
    logger.info("The SQL will be saved to scripts/articles/bulk_outline_update.sql")
    
    # For now, we'll generate the SQL structure
    # The actual articles will be fetched by the assistant
    logger.info("\n" + "="*60)
    logger.info("Next steps:")
    logger.info("1. Assistant will fetch articles with status='draft_outline'")
    logger.info("2. Assistant will call build_bulk_update_sql() with articles")
    logger.info("3. Assistant will execute the generated SQL via MCP Supabase")
    logger.info("="*60)

if __name__ == '__main__':
    main()

