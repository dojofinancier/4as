#!/usr/bin/env python3
"""
Step 4: Related Articles Script

Add 5 related articles to each article based on similarity (category, tags, keywords).

This script:
1. Fetches articles with content but no related articles (or empty related_articles)
2. Calculates similarity scores based on category, tags, and keywords
3. Selects top 5 related articles with category variety
4. Updates `related_articles` field with article IDs
5. Optionally adds a "Related Articles" section to content

Requirements:
- OpenAI API key in .env file as OPENAI_API_KEY (not used, but for consistency)
- Supabase credentials in .env file
"""

import os
import sys
import re
import logging
import time
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase package not installed. Run: pip install supabase")
    sys.exit(1)

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('related_articles.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing Supabase credentials in .env file")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def calculate_similarity_score(article1: Dict, article2: Dict) -> float:
    """Calculate similarity score between two articles."""
    score = 0.0
    
    # Category match (high weight)
    if article1.get('category') == article2.get('category'):
        score += 0.4
    
    # Tags overlap (medium weight)
    tags1 = set(article1.get('tags', []))
    tags2 = set(article2.get('tags', []))
    if tags1 and tags2:
        tag_overlap = len(tags1 & tags2) / len(tags1 | tags2) if (tags1 | tags2) else 0
        score += tag_overlap * 0.3
    
    # Keywords overlap (medium weight)
    keywords1 = set(article1.get('keywords', []))
    keywords2 = set(article2.get('keywords', []))
    if keywords1 and keywords2:
        keyword_overlap = len(keywords1 & keywords2) / len(keywords1 | keywords2) if (keywords1 | keywords2) else 0
        score += keyword_overlap * 0.3
    
    return score

def find_related_articles(article: Dict, all_articles: List[Dict], limit: int = 5) -> List[Dict]:
    """Find related articles based on similarity.
    
    Args:
        article: The article to find related articles for
        all_articles: All available articles to search from
        limit: Maximum number of related articles to return
    
    Returns:
        List of related article dictionaries
    """
    # Exclude self and articles without content
    candidates = [
        a for a in all_articles 
        if a.get('id') != article.get('id') 
        and a.get('content')  # Must have content
        and a.get('status') == 'draft'  # Include draft articles (not just published)
    ]
    
    if not candidates:
        logger.warning(f"No candidate articles found for: {article.get('title', 'Unknown')}")
        return []
    
    # Calculate similarity scores
    scored_articles = []
    for candidate in candidates:
        score = calculate_similarity_score(article, candidate)
        scored_articles.append((score, candidate))
    
    # Sort by score (descending)
    scored_articles.sort(key=lambda x: x[0], reverse=True)
    
    # Get top N, ensuring variety
    selected = []
    categories_used = set()
    
    for score, candidate in scored_articles:
        if len(selected) >= limit:
            break
        
        # Prefer variety in categories if we have enough high-scoring articles
        if len(selected) >= 3 and candidate.get('category') in categories_used:
            # Skip if we already have articles from this category
            continue
        
        selected.append(candidate)
        categories_used.add(candidate.get('category'))
    
    # If we don't have enough, fill with remaining high-scoring articles
    if len(selected) < limit:
        for score, candidate in scored_articles:
            if len(selected) >= limit:
                break
            if candidate not in selected:
                selected.append(candidate)
    
    return selected[:limit]

def add_related_articles_section(content: str, related_articles: List[Dict]) -> str:
    """Add related articles section to the end of content."""
    if not related_articles:
        return content
    
    section = "\n\n## Articles connexes\n\n"
    
    for i, article in enumerate(related_articles, 1):
        title = article.get('title', 'Article')
        slug = article.get('slug', '')
        excerpt = article.get('excerpt', '')
        
        section += f"{i}. **[{title}](/article/{slug})**"
        if excerpt:
            section += f" - {excerpt[:150]}..."
        section += "\n"
    
    return content + section

def process_article_related(article: Dict, all_articles: List[Dict]) -> Dict[str, any]:
    """Process a single article and add related articles."""
    logger.info(f"Processing related articles for: {article['title']}")
    
    related = find_related_articles(article, all_articles, limit=5)
    
    if not related:
        logger.warning(f"No related articles found for: {article['title']}")
        return {
            'slug': article['slug'],
            'success': True,
            'related_articles': [],
            'content': article.get('content', '')
        }
    
    # Add related articles section to content
    updated_content = add_related_articles_section(
        article.get('content', ''),
        related
    )
    
    # Get IDs of related articles
    related_ids = [art.get('id') for art in related if art.get('id')]
    
    return {
        'slug': article['slug'],
        'content': updated_content,
        'related_articles': related_ids,
        'success': True
    }

def fetch_articles_needing_related_articles(limit: Optional[int] = None) -> List[Dict]:
    """Fetch articles that need related articles.
    
    Returns articles that have content but no related articles (or empty related_articles).
    """
    try:
        # Fetch all articles with content and filter in Python
        # (Supabase doesn't have a good way to check for empty arrays)
        query = supabase.from_('general_articles') \
            .select('id, slug, title, category, tags, keywords, content, excerpt, related_articles, status') \
            .not_.is_('content', 'null') \
            .eq('status', 'draft')
        
        if limit:
            query = query.limit(limit * 2)  # Fetch more to account for filtering
        
        response = query.execute()
        
        if not response.data:
            logger.info("No articles found needing related articles.")
            return []
        
        # Filter in Python: articles with null or empty related_articles
        filtered_articles = [
            article for article in response.data
            if not article.get('related_articles') or len(article.get('related_articles', [])) == 0
        ]
        
        # Apply limit after filtering
        if limit and len(filtered_articles) > limit:
            filtered_articles = filtered_articles[:limit]
        
        if filtered_articles:
            logger.info(f"Fetched {len(filtered_articles)} articles needing related articles.")
            return filtered_articles
        else:
            logger.info("No articles found needing related articles.")
            return []
    
    except Exception as e:
        logger.error(f"Error fetching articles needing related articles: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def fetch_all_available_articles() -> List[Dict]:
    """Fetch all articles that can be used as related article candidates.
    
    Returns articles with content that can be linked to.
    """
    try:
        response = supabase.from_('general_articles') \
            .select('id, slug, title, category, tags, keywords, content, excerpt, status') \
            .not_.is_('content', 'null') \
            .eq('status', 'draft') \
            .execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} available articles for related article matching.")
            return response.data
        else:
            logger.warning("No available articles found for related article matching.")
            return []
    
    except Exception as e:
        logger.error(f"Error fetching all available articles: {e}")
        return []

def update_article_related_articles(slug: str, related_article_ids: List[str], updated_content: Optional[str] = None) -> bool:
    """Update article with related articles.
    
    Args:
        slug: Article slug
        related_article_ids: List of related article UUIDs
        updated_content: Optional updated content with related articles section
    
    Returns:
        True if update successful, False otherwise
    """
    try:
        update_data = {
            'related_articles': related_article_ids,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Optionally update content if provided
        if updated_content:
            update_data['content'] = updated_content
        
        result = supabase.from_('general_articles') \
            .update(update_data) \
            .eq('slug', slug) \
            .execute()
        
        if result.data:
            logger.info(f"Updated related articles for article: {slug}")
            return True
        else:
            logger.error(f"Failed to update related articles for article: {slug}")
            return False
    
    except Exception as e:
        logger.error(f"Error updating related articles for {slug}: {e}")
        return False

def main():
    """Main function to orchestrate related article generation and update."""
    logger.info("=" * 60)
    logger.info("RELATED ARTICLES GENERATION SCRIPT")
    logger.info("=" * 60)
    
    # Fetch articles needing related articles
    articles_to_process = fetch_articles_needing_related_articles()
    if not articles_to_process:
        logger.info("No articles found needing related articles. Exiting.")
        sys.exit(0)
    
    # Fetch all available articles for matching
    all_available_articles = fetch_all_available_articles()
    if len(all_available_articles) < 2:
        logger.warning("Not enough articles available for related article matching (need at least 2). Exiting.")
        sys.exit(0)
    
    stats = {
        'processed': 0,
        'success': 0,
        'failed': 0,
        'total_related_added': 0
    }
    
    for i, article in enumerate(articles_to_process, 1):
        logger.info(f"\n[{i}/{len(articles_to_process)}] Processing: {article['title']} (ID: {article['id']})")
        
        try:
            # Find related articles
            related_articles = find_related_articles(article, all_available_articles, limit=5)
            
            if not related_articles:
                logger.warning(f"No related articles found for: {article['title']}")
                stats['processed'] += 1
                # Still update with empty array to mark as processed
                if update_article_related_articles(article['slug'], []):
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
                continue
            
            # Get IDs of related articles
            related_ids = [art.get('id') for art in related_articles if art.get('id')]
            
            if not related_ids:
                logger.warning(f"No valid IDs found for related articles of: {article['title']}")
                stats['processed'] += 1
                stats['failed'] += 1
                continue
            
            # Optionally add related articles section to content
            # For now, we'll just update the related_articles field
            # The frontend can render the related articles section
            updated_content = None  # Set to None to not modify content
            
            # Update database
            if update_article_related_articles(article['slug'], related_ids, updated_content):
                stats['success'] += 1
                stats['total_related_added'] += len(related_ids)
                logger.info(f"[SUCCESS] Added {len(related_ids)} related articles to '{article['title']}'")
                logger.debug(f"Related articles: {[art.get('title') for art in related_articles]}")
            else:
                stats['failed'] += 1
                logger.error(f"[ERROR] Failed to update DB for '{article['title']}'")
            
            stats['processed'] += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.3)
        
        except Exception as e:
            logger.error(f"Error processing article {article.get('title', 'Unknown')}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            stats['processed'] += 1
            stats['failed'] += 1
    
    logger.info("\n" + "=" * 60)
    logger.info("RELATED ARTICLES GENERATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total articles processed: {stats['processed']}")
    logger.info(f"Successfully updated: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Total related articles added: {stats['total_related_added']}")
    logger.info("=" * 60)
    
    if stats['failed'] > 0:
        logger.error("Related articles generation completed with errors.")
        sys.exit(1)
    else:
        logger.info("Related articles generation completed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()

