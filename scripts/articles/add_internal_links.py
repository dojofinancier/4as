#!/usr/bin/env python3
"""
Step 3: Internal Linking Script

Add internal links between articles using AI semantic analysis.

This script:
1. Fetches articles with content but no internal links (or empty internal_links)
2. Fetches all available articles for linking
3. Uses AI to identify 3-5 relevant internal linking opportunities per article
4. Inserts links naturally into the content
5. Updates database with new content and internal_links metadata

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
import unicodedata
from typing import Dict, List, Optional, Tuple
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
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('internal_links.log', encoding='utf-8'),
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
    logger.error("Required: NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY)")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def build_linking_prompt(article_content: str, article_title: str, available_articles: List[Dict]) -> str:
    """Build the AI prompt for internal linking."""
    # Exclude the current article from available articles
    current_slug = None
    filtered_articles = []
    for art in available_articles:
        if art.get('title') == article_title:
            current_slug = art.get('slug')
        else:
            filtered_articles.append(art)
    
    # Limit to 50 articles to avoid token limits
    if len(filtered_articles) > 50:
        filtered_articles = filtered_articles[:50]
        logger.warning(f"Limited available articles to 50 (out of {len(available_articles)})")
    
    articles_list = "\n".join([
        f"- {art['title']} (slug: {art['slug']}, category: {art.get('category', 'N/A')}, tags: {', '.join(art.get('tags', [])[:3]) if art.get('tags') else 'N/A'})"
        for art in filtered_articles
    ])
    
    # Use more content for better context (up to 5000 chars)
    content_preview = article_content[:5000]
    if len(article_content) > 5000:
        content_preview += "..."
    
    prompt = f"""Tu es un expert en SEO et en rédaction de contenu. Analyse le contenu de l'article suivant et identifie 3-5 opportunités de liens internes vers d'autres articles pertinents.

**Titre de l'article actuel:** {article_title}

**Contenu de l'article actuel:**
{content_preview}

**Articles disponibles pour le lien (NE PAS inclure l'article actuel):**
{articles_list}

**Instructions CRITIQUES:**
- Identifie 3-5 endroits dans le contenu où un lien interne serait pertinent et naturel
- Choisis des articles qui sont vraiment pertinents au contexte et ajoutent de la valeur
- **TEXTE D'ANCRAGE (TRÈS IMPORTANT):** 
  * Tu DOIS copier-coller le texte EXACT qui apparaît dans le contenu ci-dessus
  * Ne modifie RIEN: pas de majuscules/minuscules, pas de ponctuation différente, pas de mots ajoutés ou retirés
  * Si le contenu dit "étudier", utilise "étudier" (pas "etudier" ou "Étudier")
  * Si le contenu dit "réviser", utilise "réviser" (pas "reviser" ou "rAcviser")
  * Copie le texte MOT PAR MOT tel qu'il apparaît dans le contenu
- Les liens doivent être naturels et contextuels - ne force pas les liens
- Évite de créer des liens vers des articles trop similaires ou redondants
- Priorise les articles de la même catégorie ou avec des tags/keywords similaires

**Format de réponse (JSON):**
{{
  "links": [
    {{
      "anchor_text": "texte exact d'ancrage qui apparaît dans le contenu",
      "target_slug": "slug-de-l-article-cible",
      "context": "brève description du contexte (ex: 'paragraphe sur les techniques de mémorisation')"
    }}
  ]
}}

Génère maintenant la réponse en JSON valide."""
    
    return prompt

def normalize_text(text: str) -> str:
    """Normalize text for better matching (handles encoding variations)."""
    # Normalize unicode
    text = unicodedata.normalize('NFD', text)
    # Remove combining marks
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().strip()

def fuzzy_match_anchor(anchor_text: str, content: str, start_pos: int = 0, search_window: int = 500) -> Optional[Tuple[int, str]]:
    """Fuzzy match anchor text, handling encoding variations.
    
    Returns tuple of (position, actual_text_found) or None.
    """
    anchor_lower = anchor_text.lower().strip()
    anchor_normalized = normalize_text(anchor_text)
    
    # Search in a window around the expected position
    search_start = max(0, start_pos - search_window // 2)
    search_end = min(len(content), start_pos + search_window // 2)
    search_content = content[search_start:search_end]
    search_content_lower = search_content.lower()
    search_content_normalized = normalize_text(search_content)
    
    # Strategy 1: Exact match in search window
    pos = search_content_lower.find(anchor_lower)
    if pos != -1:
        actual_text = search_content[pos:pos+len(anchor_text)]
        return (search_start + pos, actual_text)
    
    # Strategy 2: Normalized match
    pos = search_content_normalized.find(anchor_normalized)
    if pos != -1:
        # Find corresponding text in original (approximate)
        # Look for words from anchor in the normalized content
        anchor_words = anchor_normalized.split()
        if anchor_words:
            # Find where first significant word appears
            first_word = anchor_words[0]
            word_pos = search_content_normalized.find(first_word)
            if word_pos != -1:
                # Try to extract the actual text at this position
                # Estimate length (normalization doesn't change length much)
                estimated_length = len(anchor_text)
                actual_start = search_start + word_pos
                actual_end = min(len(content), actual_start + estimated_length + 50)
                actual_text = content[actual_start:actual_end]
                # Try to find word boundaries
                words = actual_text.split()
                if len(words) >= len(anchor_words):
                    # Take first N words matching anchor word count
                    actual_text = ' '.join(words[:len(anchor_words)])
                    return (actual_start, actual_text)
    
    # Strategy 3: Find key words from anchor text
    anchor_words = [w.strip() for w in anchor_lower.split() if len(w.strip()) > 3]
    if len(anchor_words) >= 2:
        # Find position where multiple words appear close together
        best_pos = -1
        best_score = 0
        best_text = ""
        
        for i in range(len(search_content_normalized) - 100):
            window = search_content_normalized[i:i+200]
            matching_words = [w for w in anchor_words if w in window]
            score = len(matching_words)
            
            if score > best_score and score >= len(anchor_words) * 0.6:
                best_score = score
                best_pos = search_start + i
                # Extract text around this position
                text_start = max(0, i - 20)
                text_end = min(len(search_content), i + len(anchor_text) + 20)
                best_text = search_content[text_start:text_end]
        
        if best_pos != -1:
            return (best_pos, best_text[:len(anchor_text) + 20])
    
    return None

def find_anchor_text_in_content(content: str, anchor_text: str, context: str = "") -> Optional[int]:
    """Find the best position for anchor text in content.
    
    Uses multiple strategies:
    1. Exact match (case-insensitive)
    2. Normalized match (handles encoding variations)
    3. Fuzzy matching with encoding tolerance
    4. Partial word match
    5. Context-based search
    """
    content_lower = content.lower()
    anchor_lower = anchor_text.lower().strip()
    
    # Strategy 1: Exact match (case-insensitive)
    pos = content_lower.find(anchor_lower)
    if pos != -1:
        return pos
    
    # Strategy 2: Normalized match (handles encoding variations)
    content_normalized = normalize_text(content)
    anchor_normalized = normalize_text(anchor_text)
    pos = content_normalized.find(anchor_normalized)
    if pos != -1:
        # Find corresponding position in original content
        # Approximate by finding similar text in original
        anchor_words = anchor_normalized.split()
        if anchor_words:
            # Find first word of anchor in normalized content
            first_word_pos = content_normalized.find(anchor_words[0])
            if first_word_pos != -1:
                # Map back to original content (approximate)
                # Since normalization doesn't change length much, use same position
                return first_word_pos
    
    # Strategy 3: Fuzzy match with encoding tolerance (if context provided)
    if context:
        # Try to find position from context
        context_normalized = normalize_text(context)
        context_pos = content_normalized.find(context_normalized[:50])  # First 50 chars of context
        if context_pos != -1:
            # Use fuzzy matching around context position
            fuzzy_result = fuzzy_match_anchor(anchor_text, content, context_pos, search_window=300)
            if fuzzy_result:
                return fuzzy_result[0]
    
    # Strategy 4: Partial word match - find where key words appear together
    anchor_words = [w.strip() for w in anchor_lower.split() if len(w.strip()) > 2]
    if len(anchor_words) >= 2:
        # Find position where multiple anchor words appear close together
        best_pos = -1
        best_score = 0
        
        # Search in normalized content for better matching
        for i in range(len(content_normalized) - 50):
            window = content_normalized[i:i+200]
            score = sum(1 for word in anchor_words if word in window)
            if score > best_score and score >= len(anchor_words) * 0.6:  # At least 60% of words
                best_score = score
                best_pos = i
        
        if best_pos != -1:
            return best_pos
    
    # Strategy 5: If context provided, try to find keywords from context
    if context:
        context_words = [w for w in normalize_text(context).split() if len(w) > 4]  # Only meaningful words
        if context_words:
            for word in context_words:
                pos = content_normalized.find(word)
                if pos != -1:
                    # Look for sentence boundary nearby in original content
                    for j in range(max(0, pos - 100), min(len(content), pos + 100)):
                        if content[j] in '.!?\n':
                            return j + 1
                    return pos
    
    return None

def insert_internal_links(content: str, links: List[Dict], current_slug: str) -> Tuple[str, List[Dict]]:
    """Insert internal links into content at appropriate positions.
    
    Returns:
        Tuple of (updated_content, internal_links_metadata)
    """
    # Filter out self-links
    valid_links = [link for link in links if link.get('target_slug') != current_slug]
    
    if not valid_links:
        logger.warning("No valid links to insert (all were self-links or invalid)")
        return content, []
    
    # Sort links by position in content (process from end to start to preserve positions)
    link_positions = []
    for link in valid_links:
        anchor_text = link.get('anchor_text', '')
        context = link.get('context', '')
        pos = find_anchor_text_in_content(content, anchor_text, context)
        if pos is not None:
            link_positions.append((pos, link))
    
    # Sort by position (descending) so we can insert from end to start
    link_positions.sort(key=lambda x: x[0], reverse=True)
    
    updated_content = content
    internal_links_metadata = []
    links_inserted = set()  # Track which anchor texts we've already linked
    
    for pos, link in link_positions:
        anchor_text = link.get('anchor_text', '')
        target_slug = link.get('target_slug', '')
        
        if not anchor_text or not target_slug:
            continue
        
        # Skip if we've already linked this anchor text (avoid duplicates)
        anchor_lower = anchor_text.lower()
        if anchor_lower in links_inserted:
            logger.debug(f"Skipping duplicate anchor text: {anchor_text}")
            continue
        
        # Check if this anchor text is already a link
        # Look for markdown link pattern around this position
        check_start = max(0, pos - 50)
        check_end = min(len(updated_content), pos + len(anchor_text) + 50)
        check_window = updated_content[check_start:check_end]
        
        if re.search(r'\[.*?\]\(/article/', check_window):
            logger.debug(f"Anchor text already linked: {anchor_text}")
            continue
        
        # Create markdown link
        markdown_link = f"[{anchor_text}](/article/{target_slug})"
        
        # Find the exact position of anchor text in current content
        # Try multiple strategies
        anchor_pos = None
        
        # Strategy 1: Direct search in the area
        anchor_pos = updated_content.lower().find(anchor_lower, max(0, pos - 200), min(len(updated_content), pos + 200))
        
        # Strategy 2: If not found, try normalized search
        if anchor_pos == -1:
            anchor_normalized = normalize_text(anchor_text)
            content_normalized = normalize_text(updated_content)
            normalized_pos = content_normalized.find(anchor_normalized, max(0, pos - 200), min(len(content_normalized), pos + 200))
            if normalized_pos != -1:
                anchor_pos = normalized_pos
        
        # Strategy 3: Try finding key words from anchor text
        if anchor_pos == -1:
            anchor_words = [w.strip() for w in anchor_lower.split() if len(w.strip()) > 3]
            if anchor_words:
                # Find where first significant word appears
                first_word = anchor_words[0]
                word_pos = updated_content.lower().find(first_word, max(0, pos - 300), min(len(updated_content), pos + 300))
                if word_pos != -1:
                    anchor_pos = word_pos
        
        if anchor_pos is not None and anchor_pos != -1:
            # Find the actual anchor text at this position (may have encoding differences)
            # Look for the anchor text or a close match in the content
            search_window = updated_content[max(0, anchor_pos - 20):min(len(updated_content), anchor_pos + len(anchor_text) + 20)]
            
            # Try to find exact match first
            exact_match = search_window.find(anchor_text)
            if exact_match != -1:
                actual_start = max(0, anchor_pos - 20) + exact_match
                actual_end = actual_start + len(anchor_text)
            else:
                # Try normalized match
                search_window_normalized = normalize_text(search_window)
                anchor_normalized = normalize_text(anchor_text)
                normalized_match = search_window_normalized.find(anchor_normalized)
                if normalized_match != -1:
                    # Approximate position
                    actual_start = max(0, anchor_pos - 20) + normalized_match
                    # Estimate length (normalization doesn't change length much)
                    actual_end = actual_start + len(anchor_text)
                else:
                    # Use position as-is and try to find word boundaries
                    actual_start = anchor_pos
                    # Find word boundaries
                    while actual_start > 0 and updated_content[actual_start-1] not in ' \n\t.,!?;:':
                        actual_start -= 1
                    actual_end = actual_start + len(anchor_text)
                    # Extend to word boundary
                    while actual_end < len(updated_content) and updated_content[actual_end] not in ' \n\t.,!?;:':
                        actual_end += 1
            
            # Replace anchor text with markdown link
            updated_content = (
                updated_content[:actual_start] +
                markdown_link +
                updated_content[actual_end:]
            )
            
            # Update position for metadata (use actual_start)
            anchor_pos = actual_start
            
            internal_links_metadata.append({
                'slug': target_slug,
                'anchor_text': anchor_text,
                'position': anchor_pos
            })
            
            links_inserted.add(anchor_lower)
            logger.info(f"Inserted link: '{anchor_text}' -> {target_slug} at position {anchor_pos}")
        else:
            logger.warning(f"Could not find anchor text '{anchor_text}' in content near position {pos}")
            # Log a sample of content around the position for debugging
            sample_start = max(0, pos - 100)
            sample_end = min(len(updated_content), pos + 100)
            logger.debug(f"Content sample around position {pos}: ...{updated_content[sample_start:sample_end]}...")
    
    return updated_content, internal_links_metadata

def generate_internal_links(article: Dict, available_articles: List[Dict], max_retries: int = 3) -> Dict[str, any]:
    """Generate internal links using AI with retry logic for empty responses."""
    if not article.get('content'):
        return {
            'success': False,
            'error': 'No content found'
        }
    
    # Exclude current article from available articles
    current_slug = article.get('slug')
    filtered_articles = [art for art in available_articles if art.get('slug') != current_slug]
    
    if len(filtered_articles) < 3:
        return {
            'success': False,
            'error': f'Not enough articles available for linking (need at least 3, found {len(filtered_articles)})'
        }
    
    prompt = build_linking_prompt(article['content'], article.get('title', ''), filtered_articles)
    
    # Retry logic for empty responses
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en SEO et en rédaction de contenu. Tu identifies des opportunités de liens internes naturels et pertinents qui ajoutent de la valeur au lecteur."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=2000,  # Enough for 5 links with context
                reasoning_effort="low",  # Low reasoning for faster, cost-effective responses
                verbosity="medium",  # Medium verbosity for structured JSON responses
                response_format={"type": "json_object"}
            )
            
            if not response.choices or len(response.choices) == 0:
                if attempt < max_retries - 1:
                    logger.warning(f"Empty response choices (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {
                    'success': False,
                    'error': 'No response choices'
                }
            
            response_text = response.choices[0].message.content
            if not response_text:
                if attempt < max_retries - 1:
                    logger.warning(f"Empty response text (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {
                    'success': False,
                    'error': 'Empty response'
                }
            
            # Parse JSON response
            try:
                links_data = json.loads(response_text)
                links = links_data.get('links', [])
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.error(f"Response text: {response_text[:500]}")
                if attempt < max_retries - 1:
                    logger.warning(f"JSON parse error (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'success': False,
                    'error': f'Invalid JSON response: {str(e)}'
                }
            
            if not links:
                if attempt < max_retries - 1:
                    logger.warning(f"No links in response (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'success': False,
                    'error': 'No links found in response'
                }
            
            # Validate links
            valid_links = []
            available_slugs = {art['slug'] for art in filtered_articles}
            
            for link in links:
                target_slug = link.get('target_slug')
                anchor_text = link.get('anchor_text', '').strip()
                
                if not target_slug or not anchor_text:
                    logger.warning(f"Skipping link with missing target_slug or anchor_text: {link}")
                    continue
                
                if target_slug not in available_slugs:
                    logger.warning(f"Invalid target slug: {target_slug}")
                    continue
                
                if target_slug == current_slug:
                    logger.warning(f"Skipping self-link: {target_slug}")
                    continue
                
                valid_links.append(link)
            
            if not valid_links:
                if attempt < max_retries - 1:
                    logger.warning(f"No valid links after validation (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'success': False,
                    'error': 'No valid links found after validation'
                }
            
            # Insert links into content
            updated_content, internal_links_metadata = insert_internal_links(
                article['content'],
                valid_links,
                current_slug
            )
            
            if not internal_links_metadata:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to insert links (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'success': False,
                    'error': 'Failed to insert any links into content'
                }
            
            return {
                'content': updated_content,
                'internal_links': internal_links_metadata,
                'success': True
            }
        
        except Exception as e:
            logger.error(f"Error generating internal links (attempt {attempt + 1}/{max_retries}): {e}")
            import traceback
            logger.error(traceback.format_exc())
            if attempt < max_retries - 1:
                logger.warning(f"Retrying after error...")
                time.sleep(2 ** attempt)
                continue
            return {
                'success': False,
                'error': str(e)
            }
    
    # If we get here, all retries failed
    return {
        'success': False,
        'error': f'Failed after {max_retries} attempts'
    }

def fetch_articles_needing_links(limit: Optional[int] = None) -> List[Dict]:
    """Fetch articles that need internal links."""
    try:
        query = supabase.from_('general_articles')\
            .select('id, slug, title, content, category, tags, keywords')\
            .not_.is_('content', 'null')\
            .or_('internal_links.is.null,internal_links.eq.[]')\
            .eq('status', 'draft')
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} articles needing internal links")
            return response.data
        else:
            logger.info("No articles found needing internal links")
            return []
    
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []

def fetch_all_available_articles() -> List[Dict]:
    """Fetch all articles available for linking (must have content)."""
    try:
        response = supabase.from_('general_articles')\
            .select('id, slug, title, category, tags, keywords')\
            .not_.is_('content', 'null')\
            .eq('status', 'draft')\
            .execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} articles available for linking")
            return response.data
        else:
            logger.warning("No articles available for linking")
            return []
    
    except Exception as e:
        logger.error(f"Error fetching available articles: {e}")
        return []

def update_article_links(slug: str, content: str, internal_links: List[Dict]) -> bool:
    """Update article with new content and internal links."""
    try:
        update_data = {
            'content': content,
            'internal_links': internal_links,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase.from_('general_articles')\
            .update(update_data)\
            .eq('slug', slug)\
            .execute()
        
        if result.data:
            logger.info(f"Updated internal links for article: {slug}")
            return True
        else:
            logger.error(f"Failed to update internal links for article: {slug}")
            return False
    
    except Exception as e:
        logger.error(f"Error updating article links for {slug}: {e}")
        return False

def main():
    """Main function."""
    logger.info("=" * 60)
    logger.info("INTERNAL LINKS GENERATION")
    logger.info("=" * 60)
    
    # Fetch articles needing links
    articles = fetch_articles_needing_links()
    
    if not articles:
        logger.info("No articles need internal links. Exiting.")
        sys.exit(0)
    
    # Fetch all available articles for linking
    available_articles = fetch_all_available_articles()
    
    if len(available_articles) < 3:
        logger.error(f"Not enough articles available for linking (need at least 3, found {len(available_articles)})")
        sys.exit(1)
    
    logger.info(f"Processing {len(articles)} articles...")
    logger.info(f"Available articles for linking: {len(available_articles)}")
    
    stats = {
        'processed': 0,
        'success': 0,
        'failed': 0,
        'links_added': 0
    }
    
    for i, article in enumerate(articles, 1):
        logger.info(f"\n[{i}/{len(articles)}] Processing: {article['title']}")
        
        try:
            result = generate_internal_links(article, available_articles)
            
            if not result['success']:
                logger.error(f"Failed to generate links: {result.get('error')}")
                stats['failed'] += 1
                continue
            
            # Update database
            if update_article_links(
                article['slug'],
                result['content'],
                result['internal_links']
            ):
                stats['success'] += 1
                stats['links_added'] += len(result['internal_links'])
                logger.info(f"[SUCCESS] Added {len(result['internal_links'])} internal links")
            else:
                stats['failed'] += 1
                logger.error(f"Failed to update database for: {article['slug']}")
        
        except Exception as e:
            logger.error(f"Error processing article {article.get('slug', 'unknown')}: {e}")
            stats['failed'] += 1
            continue
        
        stats['processed'] += 1
        
        # Small delay to avoid rate limiting
        if i < len(articles):
            time.sleep(0.5)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("INTERNAL LINKS GENERATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total articles processed: {stats['processed']}")
    logger.info(f"Successfully updated: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Total links added: {stats['links_added']}")
    logger.info("=" * 60)
    
    if stats['failed'] > 0:
        logger.warning(f"Completed with {stats['failed']} failures")
        sys.exit(1)
    else:
        logger.info("Internal links generation completed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()
