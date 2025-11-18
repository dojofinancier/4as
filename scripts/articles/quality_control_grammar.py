#!/usr/bin/env python3
"""
Quality Control: Grammar Check and Correction Script

This script checks and corrects grammatical errors in article titles, H1, 
meta descriptions, and excerpts. It should be run after article generation 
but before publishing.

Common issues fixed:
- "en la/le" → "en" (e.g., "en la lecture" → "en lecture")
- "de la/le" → "du/de la" when appropriate
- Other French grammar errors

Requirements:
- OpenAI API key in .env file as OPENAI_API_KEY
- Supabase credentials in .env (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY)
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

try:
    from openai import OpenAI
    from supabase import create_client, Client
except ImportError:
    print("Error: Required packages not installed. Run: pip install openai supabase")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quality_control_grammar.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("Missing OPENAI_API_KEY in .env file")
    sys.exit(1)

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing Supabase credentials. Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in your .env file.")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def build_grammar_check_prompt(title: str, h1: Optional[str] = None, 
                               meta_description: Optional[str] = None,
                               excerpt: Optional[str] = None) -> str:
    """Build the AI prompt for grammar checking and correction."""
    
    fields_to_check = []
    if title:
        fields_to_check.append(f"**Titre:** {title}")
    if h1:
        fields_to_check.append(f"**H1:** {h1}")
    if meta_description:
        fields_to_check.append(f"**Meta description:** {meta_description}")
    if excerpt:
        fields_to_check.append(f"**Extrait:** {excerpt}")
    
    fields_text = "\n".join(fields_to_check)
    
    prompt = f"""Tu es un expert en grammaire française. Corrige les erreurs grammaticales dans les champs suivants d'un article de blog.

{fields_text}

**Instructions:**
- Corrige toutes les erreurs grammaticales (articles incorrects, prépositions, accords, etc.)
- Les erreurs courantes incluent: "en la/le" → "en", "de le" → "du", etc.
- Conserve le sens et le style original
- Si un champ est déjà correct, retourne-le tel quel
- Retourne UNIQUEMENT les versions corrigées, sans explications

**Format de réponse (JSON):**
{{
  "title": "titre corrigé",
  "h1": "h1 corrigé ou identique",
  "meta_description": "meta description corrigée ou identique",
  "excerpt": "extrait corrigé ou identique"
}}

Retourne uniquement le JSON, sans texte supplémentaire."""
    
    return prompt

def check_and_correct_grammar(title: str, h1: Optional[str] = None,
                              meta_description: Optional[str] = None,
                              excerpt: Optional[str] = None) -> Dict[str, any]:
    """Check and correct grammar using OpenAI API."""
    
    prompt = build_grammar_check_prompt(title, h1, meta_description, excerpt)
    
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en grammaire française. Tu corriges les erreurs grammaticales dans les titres et descriptions d'articles de blog. Tu retournes uniquement du JSON valide."
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
            logger.error(f"No choices in response for title: {title}")
            return {
                'success': False,
                'error': 'No response choices'
            }
        
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
            corrected = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for {title}: {e}")
            logger.error(f"Response was: {response_text}")
            return {
                'success': False,
                'error': f'Invalid JSON response: {str(e)}'
            }
        
        # Validate that we got the required fields
        if 'title' not in corrected:
            logger.error(f"Missing 'title' in corrected response for {title}")
            return {
                'success': False,
                'error': 'Missing title in response'
            }
        
        # Check if any corrections were made
        changes = {}
        if corrected.get('title') != title:
            changes['title'] = corrected['title']
        if h1 and corrected.get('h1') and corrected['h1'] != h1:
            changes['h1'] = corrected['h1']
        if meta_description and corrected.get('meta_description') and corrected['meta_description'] != meta_description:
            changes['meta_description'] = corrected['meta_description']
        if excerpt and corrected.get('excerpt') and corrected['excerpt'] != excerpt:
            changes['excerpt'] = corrected['excerpt']
        
        logger.info(f"Grammar check for '{title}': {len(changes)} field(s) corrected")
        if changes:
            for field, new_value in changes.items():
                logger.info(f"  {field}: '{new_value}'")
        
        return {
            'title': corrected['title'],
            'h1': corrected.get('h1', h1),
            'meta_description': corrected.get('meta_description', meta_description),
            'excerpt': corrected.get('excerpt', excerpt),
            'changes': changes,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error checking grammar for {title}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def fetch_articles_for_grammar_check(status: Optional[str] = None, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
    """Fetch articles that need grammar checking."""
    try:
        query = supabase.from_('general_articles').select('id, slug, title, h1, meta_description, excerpt, status')
        
        if status:
            query = query.eq('status', status)
        else:
            # Default: check articles that have content (draft or published)
            query = query.in_('status', ['draft', 'published'])
        
        # Add offset for pagination
        if offset > 0:
            query = query.range(offset, offset + (limit or 50) - 1)
        elif limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} articles for grammar check (offset: {offset})")
            return response.data
        return []
        
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []

def update_article_grammar(slug: str, corrections: Dict[str, str]) -> bool:
    """Update article with grammar corrections."""
    try:
        update_data = {
            **corrections,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.from_('general_articles').update(update_data).eq('slug', slug).execute()
        
        if response.data:
            logger.info(f"✓ Updated grammar for: {slug}")
            return True
        else:
            logger.warning(f"No article found with slug: {slug}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating article {slug}: {e}")
        return False

def process_article_grammar(article: Dict) -> Dict[str, any]:
    """Process a single article and check/correct grammar."""
    logger.info(f"Checking grammar for: {article['title']}")
    
    result = check_and_correct_grammar(
        title=article['title'],
        h1=article.get('h1'),
        meta_description=article.get('meta_description'),
        excerpt=article.get('excerpt')
    )
    
    if not result['success']:
        return {
            'slug': article['slug'],
            'success': False,
            'error': result.get('error', 'Unknown error')
        }
    
    # Only update if there were changes
    if result['changes']:
        update_success = update_article_grammar(article['slug'], result['changes'])
        if not update_success:
            return {
                'slug': article['slug'],
                'success': False,
                'error': 'Failed to update database'
            }
    
    return {
        'slug': article['slug'],
        'title_original': article['title'],
        'title_corrected': result['title'],
        'changes': result['changes'],
        'success': True
    }

def main():
    """Main function to process articles in batches."""
    logger.info("=" * 60)
    logger.info("Quality Control: Grammar Check and Correction")
    logger.info("=" * 60)
    
    # Process in batches
    batch_size = 20
    total_processed = 0
    total_corrected = 0
    total_failed = 0
    
    offset = 0
    processed_slugs = set()  # Track processed articles to avoid duplicates
    
    while True:
        logger.info(f"\nFetching batch starting at offset {offset}...")
        articles = fetch_articles_for_grammar_check(limit=batch_size, offset=offset)
        
        if not articles:
            logger.info("No more articles to process.")
            break
        
        # Filter out already processed articles
        articles = [a for a in articles if a['slug'] not in processed_slugs]
        
        if not articles:
            logger.info("All articles in this batch were already processed. Moving to next batch...")
            offset += batch_size
            continue
        
        logger.info(f"Processing batch of {len(articles)} articles...")
        
        for i, article in enumerate(articles):
            total_processed += 1
            logger.info(f"\n[{total_processed}] Processing: {article['title']}")
            
            result = process_article_grammar(article)
            
            # Mark as processed
            processed_slugs.add(article['slug'])
            
            if result['success']:
                if result.get('changes'):
                    total_corrected += 1
                    logger.info(f"  ✓ Corrected: {result['changes']}")
                else:
                    logger.info(f"  ✓ No corrections needed")
            else:
                total_failed += 1
                logger.error(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        offset += batch_size
        
        # If we got fewer articles than batch_size, we're done
        if len(articles) < batch_size:
            break
        
        # Brief pause between batches
        time.sleep(1)
    
    logger.info("\n" + "=" * 60)
    logger.info("GRAMMAR CHECK SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total articles processed: {total_processed}")
    logger.info(f"Articles corrected: {total_corrected}")
    logger.info(f"Articles with no changes: {total_processed - total_corrected - total_failed}")
    logger.info(f"Articles failed: {total_failed}")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()

