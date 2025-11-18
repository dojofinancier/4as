#!/usr/bin/env python3
"""
Migration script to fix existing slugs in the database.

This script:
1. Reads all articles from the database
2. Generates new slugs using the corrected generate_slug() function
3. Updates slugs using id (UUID) to preserve all other data
4. Creates a mapping file of old_slug -> new_slug
5. Verifies data integrity after migration

Run with --dry-run first to see what would change without making changes.
"""

import os
import sys
import re
import unicodedata
import logging
import json
import argparse
from typing import Dict, List, Tuple
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
        logging.FileHandler('fix_slugs_migration.log'),
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

def fetch_all_articles() -> List[Dict]:
    """Fetch all articles from the database."""
    try:
        response = supabase.from_('general_articles')\
            .select('id, slug, title')\
            .execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} articles from database")
            return response.data
        else:
            logger.warning("No articles found in database")
            return []
    
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []

def check_slug_conflicts(new_slugs: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Check for slug conflicts. Returns dict of slug -> list of article IDs."""
    conflicts = {}
    slug_to_ids = {}
    
    for article_id, new_slug in new_slugs:
        if new_slug in slug_to_ids:
            slug_to_ids[new_slug].append(article_id)
        else:
            slug_to_ids[new_slug] = [article_id]
    
    # Find conflicts (same slug for different articles)
    for slug, ids in slug_to_ids.items():
        if len(ids) > 1:
            conflicts[slug] = ids
    
    return conflicts

def resolve_slug_conflict(base_slug: str, existing_slugs: set, counter: int = 1) -> str:
    """Resolve slug conflict by appending a number."""
    new_slug = f"{base_slug}-{counter}"
    if new_slug in existing_slugs:
        return resolve_slug_conflict(base_slug, existing_slugs, counter + 1)
    return new_slug

def generate_migration_plan(articles: List[Dict], dry_run: bool = True) -> Dict:
    """Generate migration plan with old and new slugs."""
    logger.info("=" * 60)
    logger.info("GENERATING MIGRATION PLAN")
    logger.info("=" * 60)
    
    migration_plan = []
    changes_needed = 0
    
    for article in articles:
        old_slug = article['slug']
        new_slug = generate_slug(article['title'])
        
        if old_slug != new_slug:
            changes_needed += 1
            migration_plan.append({
                'id': article['id'],
                'title': article['title'],
                'old_slug': old_slug,
                'new_slug': new_slug,
                'changed': True
            })
        else:
            migration_plan.append({
                'id': article['id'],
                'title': article['title'],
                'old_slug': old_slug,
                'new_slug': new_slug,
                'changed': False
            })
    
    logger.info(f"Total articles: {len(articles)}")
    logger.info(f"Articles needing slug update: {changes_needed}")
    logger.info(f"Articles with correct slugs: {len(articles) - changes_needed}")
    
    # Check for conflicts
    new_slugs = [(item['id'], item['new_slug']) for item in migration_plan]
    conflicts = check_slug_conflicts(new_slugs)
    
    if conflicts:
        logger.warning(f"Found {len(conflicts)} slug conflicts that need resolution:")
        for slug, ids in conflicts.items():
            logger.warning(f"  Slug '{slug}' would be used by {len(ids)} articles")
        
        # Resolve conflicts
        existing_slugs = set(item['new_slug'] for item in migration_plan if not item['changed'])
        for item in migration_plan:
            if item['changed']:
                # Check if this slug conflicts
                conflicting_items = [x for x in migration_plan if x['new_slug'] == item['new_slug'] and x['id'] != item['id']]
                if conflicting_items:
                    # Resolve conflict
                    base_slug = item['new_slug']
                    all_new_slugs = set(x['new_slug'] for x in migration_plan)
                    item['new_slug'] = resolve_slug_conflict(base_slug, all_new_slugs)
                    logger.info(f"Resolved conflict: '{base_slug}' -> '{item['new_slug']}' for article: {item['title'][:50]}")
    else:
        logger.info("No slug conflicts detected [OK]")
    
    return {
        'plan': migration_plan,
        'changes_needed': changes_needed,
        'conflicts_resolved': len(conflicts) > 0
    }

def execute_migration(migration_plan: List[Dict], dry_run: bool = True) -> Dict:
    """Execute the migration plan."""
    stats = {
        'total': len(migration_plan),
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'mapping': {}
    }
    
    logger.info("=" * 60)
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made to database")
    else:
        logger.info("EXECUTING MIGRATION")
    logger.info("=" * 60)
    
    for i, item in enumerate(migration_plan, 1):
        if not item['changed']:
            stats['skipped'] += 1
            continue
        
        old_slug = item['old_slug']
        new_slug = item['new_slug']
        article_id = item['id']
        
        logger.info(f"[{i}/{stats['total']}] Updating slug for: {item['title'][:50]}...")
        logger.info(f"  Old: {old_slug}")
        logger.info(f"  New: {new_slug}")
        
        if dry_run:
            stats['updated'] += 1
            stats['mapping'][old_slug] = new_slug
            logger.info("  [DRY RUN] Would update")
        else:
            try:
                # Update using id (UUID) to preserve all other data
                result = supabase.from_('general_articles')\
                    .update({'slug': new_slug})\
                    .eq('id', article_id)\
                    .execute()
                
                if result.data:
                    stats['updated'] += 1
                    stats['mapping'][old_slug] = new_slug
                    logger.info("  [SUCCESS] Updated successfully")
                else:
                    stats['errors'] += 1
                    logger.error(f"  [ERROR] Failed to update (no data returned)")
            
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"  [ERROR] Error updating: {e}")
    
    return stats

def verify_migration(migration_plan: List[Dict]) -> bool:
    """Verify that all slugs were updated correctly."""
    logger.info("=" * 60)
    logger.info("VERIFYING MIGRATION")
    logger.info("=" * 60)
    
    try:
        # Fetch all articles again
        articles = fetch_all_articles()
        
        # Create lookup by id
        articles_by_id = {art['id']: art for art in articles}
        
        verification_passed = True
        mismatches = []
        
        for item in migration_plan:
            article_id = item['id']
            expected_slug = item['new_slug']
            
            if article_id in articles_by_id:
                actual_slug = articles_by_id[article_id]['slug']
                if actual_slug != expected_slug:
                    verification_passed = False
                    mismatches.append({
                        'id': article_id,
                        'title': item['title'],
                        'expected': expected_slug,
                        'actual': actual_slug
                    })
        
        if verification_passed:
            logger.info("[SUCCESS] All slugs verified successfully!")
            return True
        else:
            logger.error(f"[ERROR] Found {len(mismatches)} mismatches:")
            for mismatch in mismatches:
                logger.error(f"  {mismatch['title'][:50]}: expected '{mismatch['expected']}', got '{mismatch['actual']}'")
            return False
    
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        return False

def save_mapping_file(mapping: Dict[str, str], filename: str = 'slug_migration_mapping.json'):
    """Save the old_slug -> new_slug mapping to a file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'migration_date': datetime.now().isoformat(),
                'total_mappings': len(mapping),
                'mappings': mapping
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Mapping file saved to: {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving mapping file: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Fix slugs in database')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would change without making changes')
    parser.add_argument('--execute', action='store_true',
                       help='Actually execute the migration (use with caution!)')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt (use with --execute)')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        logger.error("Must specify either --dry-run or --execute")
        logger.error("  --dry-run: Show what would change (safe)")
        logger.error("  --execute: Actually update the database (use with caution!)")
        sys.exit(1)
    
    dry_run = not args.execute
    
    logger.info("=" * 60)
    logger.info("SLUG MIGRATION SCRIPT")
    logger.info("=" * 60)
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    logger.info("=" * 60)
    
    # Fetch all articles
    articles = fetch_all_articles()
    
    if not articles:
        logger.error("No articles found. Exiting.")
        sys.exit(1)
    
    # Generate migration plan
    plan_result = generate_migration_plan(articles, dry_run)
    migration_plan = plan_result['plan']
    
    if plan_result['changes_needed'] == 0:
        logger.info("No changes needed - all slugs are already correct!")
        sys.exit(0)
    
    # Show preview of changes
    logger.info("\nPreview of changes (first 10):")
    changed_items = [item for item in migration_plan if item['changed']]
    for item in changed_items[:10]:
        logger.info(f"  '{item['old_slug']}' -> '{item['new_slug']}'")
        logger.info(f"    Title: {item['title'][:60]}")
    
    if len(changed_items) > 10:
        logger.info(f"  ... and {len(changed_items) - 10} more")
    
    if dry_run:
        logger.info("\n" + "=" * 60)
        logger.info("DRY RUN COMPLETE")
        logger.info("=" * 60)
        logger.info("To execute the migration, run:")
        logger.info("  python fix_slugs_migration.py --execute")
        sys.exit(0)
    
    # Ask for confirmation (unless --force is used)
    if not args.force:
        logger.info("\n" + "=" * 60)
        logger.warning("WARNING: This will update slugs in the database!")
        logger.info("=" * 60)
        try:
            response = input("Type 'YES' to confirm: ")
            if response != 'YES':
                logger.info("Migration cancelled.")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            logger.error("Migration cancelled (no input available). Use --force to skip confirmation.")
            sys.exit(1)
    else:
        logger.info("\n" + "=" * 60)
        logger.warning("WARNING: This will update slugs in the database!")
        logger.info("Running with --force flag (skipping confirmation)")
        logger.info("=" * 60)
    
    # Execute migration
    stats = execute_migration(migration_plan, dry_run=False)
    
    # Save mapping file
    if stats['mapping']:
        save_mapping_file(stats['mapping'])
    
    # Verify migration
    if stats['errors'] == 0:
        verify_migration(migration_plan)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total articles: {stats['total']}")
    logger.info(f"Updated: {stats['updated']}")
    logger.info(f"Skipped (no change needed): {stats['skipped']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info("=" * 60)
    
    if stats['errors'] > 0:
        logger.warning(f"Migration completed with {stats['errors']} errors")
        sys.exit(1)
    else:
        logger.info("Migration completed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()

