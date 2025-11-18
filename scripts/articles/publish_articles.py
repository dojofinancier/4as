#!/usr/bin/env python3
"""
Publish Articles Script

This script:
1. Fetches articles with status='draft' that have content
2. Generates tags and keywords using AI
3. Sets author to "Carré d'As Tutorat"
4. Publishes articles (status='published', published=true, published_at)
5. Generates JSON-LD if missing

Requirements:
- OpenAI API key in .env file as OPENAI_API_KEY
- Supabase credentials in .env file
"""

import os
import sys
import json
import re
import logging
import time
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

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
        logging.FileHandler('article_publishing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("Missing OPENAI_API_KEY in .env file")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing Supabase credentials in .env file")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_tags_and_keywords(title: str, category: str, content: str) -> Dict[str, List[str]]:
    """Generate tags and keywords using AI."""
    # Use first 3000 chars of content for context
    content_preview = content[:3000]
    if len(content) > 3000:
        content_preview += "..."
    
    prompt = f"""Tu es un expert en SEO et en marketing de contenu. Analyse l'article suivant et génère des tags et mots-clés pertinents.

**Titre:** {title}
**Catégorie:** {category}

**Contenu (extrait):**
{content_preview}

**Instructions:**
- Génère 5-8 tags pertinents (mots ou courtes phrases décrivant les sujets principaux)
- Génère 8-12 mots-clés SEO (phrases de recherche que les utilisateurs pourraient utiliser)
- Les tags doivent être des sujets/topics (ex: "révision", "productivité", "examens", "gestion du temps")
- Les mots-clés doivent être des phrases de recherche (ex: "comment réviser efficacement", "techniques d'étude pour étudiants")
- Tous en français
- Pertinents pour le contenu de l'article

**Format de réponse (JSON):**
{{
  "tags": ["tag1", "tag2", "tag3", ...],
  "keywords": ["mot-clé 1", "mot-clé 2", "mot-clé 3", ...]
}}

Retourne uniquement le JSON, sans texte supplémentaire."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en SEO et en marketing de contenu. Tu génères des tags et mots-clés pertinents pour des articles de blog. Tu retournes uniquement du JSON valide."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=500,
            reasoning_effort="minimal",
            verbosity="low",
            response_format={"type": "json_object"}
        )
        
        if not response.choices or len(response.choices) == 0:
            logger.error("No response choices for tags/keywords generation")
            return {'tags': [], 'keywords': []}
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean response (remove markdown code blocks if present)
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        if response_text.endswith('```'):
            response_text = response_text.rsplit('```', 1)[0].strip()
        
        # Parse JSON response
        try:
            result = json.loads(response_text)
            tags = result.get('tags', [])
            keywords = result.get('keywords', [])
            
            # Validate and clean
            tags = [tag.strip() for tag in tags if tag and isinstance(tag, str)][:8]
            keywords = [kw.strip() for kw in keywords if kw and isinstance(kw, str)][:12]
            
            logger.info(f"Generated {len(tags)} tags and {len(keywords)} keywords")
            return {'tags': tags, 'keywords': keywords}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for tags/keywords: {e}")
            logger.error(f"Response was: {response_text}")
            return {'tags': [], 'keywords': []}
        
    except Exception as e:
        logger.error(f"Error generating tags/keywords: {e}")
        return {'tags': [], 'keywords': []}

def generate_json_ld(article: Dict) -> Dict:
    """Generate JSON-LD structured data for SEO."""
    canonical_url = f"https://carredastutorat.com/article/{article['slug']}"
    
    json_ld = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': article.get('h1') or article.get('title', ''),
        'description': article.get('meta_description') or article.get('excerpt', ''),
        'author': {
            '@type': 'Organization',
            'name': "Carré d'As Tutorat"
        },
        'publisher': {
            '@type': 'Organization',
            'name': "Carré d'As Tutorat",
            'logo': {
                '@type': 'ImageObject',
                'url': 'https://carredastutorat.com/dark_logo.png'
            }
        },
        'datePublished': article.get('published_at') or article.get('created_at', ''),
        'dateModified': article.get('updated_at', ''),
        'mainEntityOfPage': {
            '@type': 'WebPage',
            '@id': canonical_url
        },
        'articleSection': article.get('category', ''),
    }
    
    if article.get('keywords'):
        json_ld['keywords'] = ', '.join(article['keywords'])
    
    if article.get('featured_image_url'):
        json_ld['image'] = article['featured_image_url']
    
    return json_ld

def count_words(text: str) -> int:
    """Count words in text."""
    text = re.sub(r'[#*`\[\]()]', '', text)
    text = re.sub(r'\n+', ' ', text)
    words = text.split()
    return len(words)

def fetch_articles_for_publishing(limit: Optional[int] = None) -> List[Dict]:
    """Fetch articles ready for publishing."""
    try:
        query = supabase.from_('general_articles') \
            .select('id, slug, title, category, content, tags, keywords, meta_description, excerpt, h1, status, published, published_at, created_at, updated_at, word_count, json_ld') \
            .eq('status', 'draft') \
            .not_.is_('content', 'null')
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} articles ready for publishing")
            return response.data
        return []
        
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []

def update_article_publishing(slug: str, update_data: Dict) -> bool:
    """Update article with publishing data."""
    try:
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        result = supabase.from_('general_articles') \
            .update(update_data) \
            .eq('slug', slug) \
            .execute()
        
        if result.data:
            logger.info(f"Published article: {slug}")
            return True
        else:
            logger.error(f"Failed to publish article: {slug}")
            return False
    
    except Exception as e:
        logger.error(f"Error updating article {slug}: {e}")
        return False

def process_article_publishing(article: Dict) -> Dict[str, any]:
    """Process a single article for publishing."""
    logger.info(f"\nProcessing: {article['title']}")
    
    # Generate tags and keywords if missing
    tags = article.get('tags', [])
    keywords = article.get('keywords', [])
    
    if not tags or not keywords or len(tags) == 0 or len(keywords) == 0:
        logger.info("Generating tags and keywords...")
        result = generate_tags_and_keywords(
            title=article['title'],
            category=article.get('category', ''),
            content=article.get('content', '')
        )
        tags = result['tags'] if not tags or len(tags) == 0 else tags
        keywords = result['keywords'] if not keywords or len(keywords) == 0 else keywords
        time.sleep(1)  # Rate limiting
    
    # Generate JSON-LD if missing
    json_ld = article.get('json_ld')
    if not json_ld:
        json_ld = generate_json_ld(article)
    
    # Count words if missing
    word_count = article.get('word_count')
    if not word_count:
        word_count = count_words(article.get('content', ''))
    
    # Prepare update data
    update_data = {
        'tags': tags,
        'keywords': keywords,
        'author': "Carré d'As Tutorat",
        'json_ld': json_ld,
        'word_count': word_count,
        'published': True,
        'status': 'published',
        'is_indexable': True
    }
    
    # Set published_at if not set
    if not article.get('published_at'):
        update_data['published_at'] = datetime.now(timezone.utc).isoformat()
    
    # Update database
    success = update_article_publishing(article['slug'], update_data)
    
    if success:
        return {
            'slug': article['slug'],
            'success': True,
            'tags_count': len(tags),
            'keywords_count': len(keywords)
        }
    else:
        return {
            'slug': article['slug'],
            'success': False,
            'error': 'Failed to update database'
        }

def main():
    """Main function to publish articles."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Publish articles with tags, keywords, and author')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of articles to process (for testing)')
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("ARTICLE PUBLISHING SCRIPT")
    logger.info("=" * 60)
    if args.limit:
        logger.info(f"TESTING MODE: Processing {args.limit} articles only")
    logger.info("=" * 60)
    
    # Fetch articles ready for publishing
    articles_to_process = fetch_articles_for_publishing(limit=args.limit)
    if not articles_to_process:
        logger.info("No articles found ready for publishing. Exiting.")
        sys.exit(0)
    
    stats = {
        'processed': 0,
        'success': 0,
        'failed': 0
    }
    
    # Process each article
    for i, article in enumerate(articles_to_process, 1):
        logger.info(f"\n[{i}/{len(articles_to_process)}] Processing: {article['title']}")
        
        stats['processed'] += 1
        
        result = process_article_publishing(article)
        
        if result['success']:
            stats['success'] += 1
            logger.info(f"[SUCCESS] Published '{article['title']}'")
            logger.info(f"  Tags: {result.get('tags_count', 0)}, Keywords: {result.get('keywords_count', 0)}")
        else:
            stats['failed'] += 1
            logger.error(f"[FAILED] {article['title']}: {result.get('error', 'Unknown error')}")
        
        # Small delay to avoid rate limits
        time.sleep(0.5)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PUBLISHING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total articles processed: {stats['processed']}")
    logger.info(f"Successfully published: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
