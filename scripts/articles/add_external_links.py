#!/usr/bin/env python3
"""
Step 5: External Links Script

Add external links and resources using AI (with validation).

This script:
1. Fetches articles with content but no external links (or empty external_links)
2. Uses AI to suggest 5-10 relevant external links (academic sources, tools, official resources)
3. Validates URLs for accessibility
4. Updates `external_links` field with link metadata
5. Optionally adds a "Resources" section to content

Requirements:
- OpenAI API key in .env file as OPENAI_API_KEY
- Supabase credentials in .env file
- requests library for URL validation
"""

import os
import sys
import json
import re
import logging
import time
import concurrent.futures
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests package not installed. Run: pip install requests")
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
        logging.FileHandler('external_links.log', encoding='utf-8'),
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

def validate_url(url: str, timeout: int = 5, max_retries: int = 2) -> bool:
    """Validate that a URL exists and is accessible.
    
    Uses HEAD request first, falls back to GET if HEAD fails.
    Includes retry logic and proper user-agent header.
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check URL format
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Try HEAD request first (faster)
        for attempt in range(max_retries):
            try:
                response = requests.head(
                    url, 
                    timeout=timeout, 
                    allow_redirects=True,
                    headers=headers
                )
                if response.status_code < 400:
                    return True
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
        
        # Fallback to GET request if HEAD fails
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    timeout=timeout,
                    allow_redirects=True,
                    headers=headers,
                    stream=True  # Don't download full content
                )
                if response.status_code < 400:
                    return True
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
        
        return False
        
    except Exception as e:
        logger.debug(f"URL validation failed for {url}: {e}")
        return False

def validate_urls_parallel(urls: List[str], max_workers: int = 5) -> Dict[str, bool]:
    """Validate multiple URLs in parallel.
    
    Returns a dictionary mapping URL to validation result.
    """
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(validate_url, url): url for url in urls}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                logger.debug(f"Error validating URL {url}: {e}")
                results[url] = False
    
    return results

def build_external_links_prompt(article_content: str, article_title: str, category: str = "") -> str:
    """Build the AI prompt for external links generation."""
    category_context = f"\n**Catégorie de l'article:** {category}" if category else ""
    
    prompt = f"""Tu es un expert en rédaction de contenu éducatif pour étudiants en gestion au Québec. Analyse le contenu de l'article suivant et suggère 5-10 liens externes pertinents, SPÉCIFIQUES et RÉELS.

**Titre de l'article:** {article_title}
{category_context}

**Contenu de l'article:**
{article_content[:5000]}

**⚠️ IMPORTANT - COMMENT GÉNÉRER DES URLS:**
- Le modèle n'a PAS d'accès internet en temps réel
- Tu dois suggérer UNIQUEMENT des URLs de sites BIEN CONNUS et STABLES que tu connais avec CERTITUDE
- Ne génère JAMAIS d'URLs que tu n'es pas ABSOLUMENT CERTAIN qu'elles existent et sont accessibles
- Privilégie des sites majeurs et populaires avec des URLs stables (ex: Wikipedia, outils populaires comme Notion, Anki, etc.)
- Si tu n'es pas sûr qu'une URL existe, NE LA SUGGÈRE PAS

**Instructions CRITIQUES:**
- Suggère UNIQUEMENT des URLs RÉELLES, ACCESSIBLES et BIEN CONNUES (pas de liens inventés, fictifs ou incertains)
- **ÉVITE ABSOLUMENT les pages d'accueil génériques** (ex: hec.ca, ulaval.ca, gouvernement.qc.ca)
- Privilégie des ressources SPÉCIFIQUES et ACTIONNABLES directement liées au contenu de l'article
- **RÈGLE ABSOLUE:** Ne suggère QUE des URLs de sites majeurs et populaires dont tu es CERTAIN de l'existence

**Types de sources à privilégier (SPÉCIFIQUES):**
- **Outils pratiques gratuits:** applications web spécifiques, calculateurs en ligne, générateurs, templates téléchargeables
  * Exemples: calculateur de GPA, générateur de CV, templates Excel/Google Sheets, outils de gestion de temps
- **Articles/guides spécifiques:** pages d'articles, guides pratiques, tutoriels (pas les pages d'accueil)
  * Exemples: "Comment faire X" sur un site spécialisé, guides pratiques, articles de blog pertinents
- **Bases de données/ressources spécifiques:** pages spécifiques de bases de données, catalogues, répertoires
  * Exemples: pages spécifiques de Statistique Canada, bases de données académiques avec articles spécifiques
- **Applications/logiciels:** liens vers des applications web gratuites spécifiques mentionnées dans l'article
  * Exemples: Notion, Obsidian, Anki, applications de productivité spécifiques
- **Ressources officielles spécifiques:** pages spécifiques de sites gouvernementaux (pas les pages d'accueil)
  * Exemples: pages spécifiques sur les prêts étudiants, programmes d'aide, formulaires officiels

**RÈGLES STRICTES:**
- ❌ INTERDIT: Pages d'accueil de sites (hec.ca, ulaval.ca, gouvernement.qc.ca, etc.)
- ❌ INTERDIT: Liens génériques non spécifiques au contenu
- ✅ REQUIS: Liens vers des pages/articles/outils SPÉCIFIQUES et directement pertinents
- ✅ REQUIS: Chaque lien doit ajouter une valeur concrète et actionnable au lecteur
- ✅ REQUIS: URL complète (https://...) vers la page spécifique, pas la page d'accueil

**Exemples de BONNES sources (spécifiques et bien connues):**
- https://www.notion.so/product (page produit spécifique, site populaire et stable)
- https://ankiweb.net/shared/decks/ (décks Anki partagés, ressource spécifique et bien connue)
- https://fr.wikipedia.org/wiki/... (articles Wikipedia spécifiques - URLs stables)
- https://www.toggl.com/blog/... (articles de blog spécifiques sur des sites populaires)
- https://www.canada.ca/fr/emploi-developpement-social/services/etudiants/aide-financiere-aux-etudes.html (page gouvernementale spécifique et stable)

**⚠️ ÉVITE ces types d'URLs (souvent invalides ou inaccessibles):**
- URLs de pages internes d'universités (ex: mcgill.ca/academic-skills) - souvent changent ou nécessitent authentification
- URLs de sites professionnels avec chemins complexes (ex: cma.ca/sections/...) - peuvent être incorrectes
- URLs de pages de support avec IDs spécifiques (ex: support.google.com/docs/answer/70618) - peuvent être obsolètes

**Exemples de MAUVAISES sources (à éviter):**
- ❌ https://www.hec.ca/ (page d'accueil générique)
- ❌ https://www.ulaval.ca/ (page d'accueil générique)
- ❌ https://www.gouvernement.qc.ca/ (page d'accueil générique)

**Format de réponse (JSON):**
{{
  "links": [
    {{
      "url": "https://example.com/specific-page-or-tool",
      "anchor_text": "texte d'ancrage naturel et spécifique",
      "description": "Description courte de la ressource spécifique (max 100 caractères)",
      "position_description": "description de l'endroit dans le texte où placer le lien"
    }}
  ]
}}

**RÈGLE ABSOLUE:** Ne génère QUE des URLs de sites MAJEURS et POPULAIRES dont tu es ABSOLUMENT CERTAIN qu'elles existent et sont accessibles. Privilégie Wikipedia, outils populaires (Notion, Anki, Toggl), et pages gouvernementales stables. Si tu doutes, NE SUGGÈRE PAS le lien."""
    
    return prompt

def generate_external_links(article_content: str, article_title: str, category: str = "", max_retries: int = 3) -> Dict[str, any]:
    """Generate external links using AI with retry logic."""
    prompt = build_external_links_prompt(article_content, article_title, category)
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en rédaction de contenu éducatif. Tu suggères UNIQUEMENT des liens externes RÉELS, ACCESSIBLES et SPÉCIFIQUES vers des ressources actionnables. RÈGLE ABSOLUE: Ne génère QUE des URLs de sites MAJEURS et POPULAIRES dont tu es CERTAIN qu'elles existent (ex: Wikipedia, Notion, Anki, Toggl, pages gouvernementales stables). Ne génère JAMAIS de liens vers des pages d'accueil génériques (ex: hec.ca, ulaval.ca) ou des URLs incertaines. Si tu doutes qu'une URL existe, NE LA SUGGÈRE PAS."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=2000,
                reasoning_effort="low",
                verbosity="medium",
                response_format={"type": "json_object"}
            )
            
            if not response.choices or len(response.choices) == 0:
                if attempt < max_retries - 1:
                    logger.warning(f"Empty response choices (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'success': False,
                    'error': 'No response choices'
                }
            
            response_text = response.choices[0].message.content
            if not response_text:
                if attempt < max_retries - 1:
                    logger.warning(f"Empty response text (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)
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
            
            # Filter out generic homepage links (safety net)
            generic_homepages = [
                'hec.ca/', 'ulaval.ca/', 'usherbrooke.ca/', 'mcgill.ca/',
                'gouvernement.qc.ca/', 'quebec.ca/', 'canada.ca/',
                'statcan.gc.ca/', 'cma.ca/'
            ]
            
            filtered_links = []
            for link in links:
                url = link.get('url', '').lower()
                if not url:
                    continue
                
                # Check if it's a generic homepage (ends with domain or has <= 3 slashes)
                is_generic = False
                for homepage in generic_homepages:
                    if homepage in url:
                        # Check if it's just the homepage (few path segments)
                        path_segments = url.split('/')
                        # Remove empty segments and protocol/domain
                        meaningful_segments = [s for s in path_segments if s and 'http' not in s and '.' not in s]
                        if len(meaningful_segments) <= 1:  # Just domain or domain + one segment
                            is_generic = True
                            break
                
                if is_generic:
                    logger.warning(f"Rejected generic homepage link: {link.get('url')}")
                    continue
                
                filtered_links.append(link)
            
            if not filtered_links:
                if attempt < max_retries - 1:
                    logger.warning(f"All links were generic homepages (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'success': False,
                    'error': 'All generated links were generic homepages (rejected)'
                }
            
            # Extract URLs from filtered links for validation
            urls = [link.get('url', '') for link in filtered_links if link.get('url')]
            
            if not urls:
                return {
                    'success': False,
                    'error': 'No URLs found in links after filtering'
                }
            
            # Validate URLs in parallel
            logger.info(f"Validating {len(urls)} URLs...")
            validation_results = validate_urls_parallel(urls, max_workers=5)
            
            # Filter valid links
            valid_links = []
            for link in filtered_links:
                url = link.get('url', '')
                if not url:
                    continue
                
                if validation_results.get(url, False):
                    valid_links.append(link)
                    logger.info(f"Validated external link: {url}")
                else:
                    logger.warning(f"Invalid or inaccessible URL: {url}")
            
            if not valid_links:
                if attempt < max_retries - 1:
                    logger.warning(f"No valid links found (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** attempt)
                    continue
                return {
                    'success': False,
                    'error': 'No valid external links found after validation'
                }
            
            return {
                'links': valid_links,
                'success': True
            }
        
        except Exception as e:
            logger.error(f"Error generating external links (attempt {attempt + 1}/{max_retries}): {e}")
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

def find_link_positions(content: str, position_descriptions: List[str]) -> List[int]:
    """Find approximate character positions for links."""
    positions = []
    content_lower = content.lower()
    
    for desc in position_descriptions:
        keywords = desc.lower().split()
        best_pos = -1
        best_score = 0
        
        for i in range(len(content_lower) - 50):
            window = content_lower[i:i+200]
            score = sum(1 for kw in keywords if kw in window)
            if score > best_score:
                best_score = score
                best_pos = i
        
        if best_pos >= 0:
            positions.append(best_pos)
        else:
            positions.append(len(content) // (len(position_descriptions) + 1) * (len(positions) + 1))
    
    return positions

def insert_external_links(content: str, links: List[Dict]) -> tuple[str, List[Dict]]:
    """Insert external links into content and create resources section."""
    if not links:
        return content, []
    
    # Sort links by position
    sorted_links = sorted(links, key=lambda x: x.get('position', 0))
    
    # Find positions
    positions = find_link_positions(content, [link.get('position_description', '') for link in sorted_links])
    
    # Insert links (from end to start)
    external_links_metadata = []
    inserted_count = 0
    
    for i, link in enumerate(reversed(sorted_links)):
        url = link['url']
        anchor_text = link['anchor_text']
        description = link.get('description', '')
        
        # Find insertion position
        pos = positions[len(positions) - 1 - i] if i < len(positions) else len(content) // 2
        
        # Try to find anchor text in content
        search_text = anchor_text.lower()
        actual_pos = content.lower().find(search_text, max(0, pos - 100), min(len(content), pos + 100))
        
        if actual_pos == -1:
            # Find sentence end near position
            for j in range(max(0, pos - 50), min(len(content), pos + 50)):
                if content[j] in '.!?':
                    actual_pos = j + 1
                    break
        
        if actual_pos == -1:
            actual_pos = pos
        
        # Create markdown link
        markdown_link = f"[{anchor_text}]({url})"
        
        # Insert link
        if search_text in content.lower():
            pattern = re.compile(re.escape(anchor_text), re.IGNORECASE)
            content = pattern.sub(markdown_link, content, count=1)
            actual_pos = content.lower().find(markdown_link.lower())
        else:
            if actual_pos < len(content):
                content = content[:actual_pos] + f" {markdown_link} " + content[actual_pos:]
                actual_pos = actual_pos + len(markdown_link) + 2
        
        external_links_metadata.append({
            'url': url,
            'anchor_text': anchor_text,
            'description': description,
            'position': actual_pos
        })
        inserted_count += 1
    
    # Add resources section at the end
    resources_section = "\n\n## Ressources externes\n\n"
    for link in links:
        resources_section += f"- **[{link['anchor_text']}]({link['url']})**"
        if link.get('description'):
            resources_section += f" - {link['description']}"
        resources_section += "\n"
    
    content = content + resources_section
    
    return content, external_links_metadata

def process_article_external_links(article: Dict) -> Dict[str, any]:
    """Process a single article and add external links."""
    logger.info(f"Processing external links for: {article['title']}")
    
    if not article.get('content'):
        return {
            'slug': article['slug'],
            'success': False,
            'error': 'No content found'
        }
    
    result = generate_external_links(
        article['content'],
        article.get('title', ''),
        article.get('category', '')
    )
    
    if not result['success']:
        return {
            'slug': article['slug'],
            'success': False,
            'error': result.get('error', 'Unknown error')
        }
    
    # Create external links metadata (without modifying content)
    # The frontend can render the links section
    external_links_metadata = []
    for link in result['links']:
        external_links_metadata.append({
            'url': link.get('url', ''),
            'anchor_text': link.get('anchor_text', ''),
            'description': link.get('description', ''),
            'position': 0  # Position not critical for external links
        })
    
    return {
        'slug': article['slug'],
        'external_links': external_links_metadata,
        'success': True
    }

def fetch_articles_needing_external_links(limit: Optional[int] = None) -> List[Dict]:
    """Fetch articles that need external links.
    
    Returns articles that have content but no external links (or empty external_links).
    """
    try:
        # Fetch all articles with content and filter in Python
        # (Supabase doesn't have a good way to check for empty JSONB arrays)
        query = supabase.from_('general_articles') \
            .select('id, slug, title, category, content, external_links, status') \
            .not_.is_('content', 'null') \
            .eq('status', 'draft')
        
        if limit:
            query = query.limit(limit * 2)  # Fetch more to account for filtering
        
        response = query.execute()
        
        if not response.data:
            logger.info("No articles found needing external links.")
            return []
        
        # Filter in Python: articles with null or empty external_links
        filtered_articles = [
            article for article in response.data
            if not article.get('external_links') or len(article.get('external_links', [])) == 0
        ]
        
        # Apply limit after filtering
        if limit and len(filtered_articles) > limit:
            filtered_articles = filtered_articles[:limit]
        
        if filtered_articles:
            logger.info(f"Fetched {len(filtered_articles)} articles needing external links.")
            return filtered_articles
        else:
            logger.info("No articles found needing external links.")
            return []
    
    except Exception as e:
        logger.error(f"Error fetching articles needing external links: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def update_article_external_links(slug: str, external_links: List[Dict], updated_content: Optional[str] = None) -> bool:
    """Update article with external links.
    
    Args:
        slug: Article slug
        external_links: List of external link metadata dictionaries
        updated_content: Optional updated content (if we want to add resources section)
    
    Returns:
        True if update successful, False otherwise
    """
    try:
        update_data = {
            'external_links': external_links,
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
            logger.info(f"Updated external links for article: {slug}")
            return True
        else:
            logger.error(f"Failed to update external links for article: {slug}")
            return False
    
    except Exception as e:
        logger.error(f"Error updating external links for {slug}: {e}")
        return False

def main():
    """Main function to orchestrate external link generation and update."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate external links for articles')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of articles to process (for testing)')
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("EXTERNAL LINKS GENERATION SCRIPT")
    logger.info("=" * 60)
    if args.limit:
        logger.info(f"TESTING MODE: Processing {args.limit} articles only")
    logger.info("=" * 60)
    
    # Fetch articles needing external links
    articles_to_process = fetch_articles_needing_external_links(limit=args.limit)
    if not articles_to_process:
        logger.info("No articles found needing external links. Exiting.")
        sys.exit(0)
    
    stats = {
        'processed': 0,
        'success': 0,
        'failed': 0,
        'total_links_added': 0
    }
    
    for i, article in enumerate(articles_to_process, 1):
        logger.info(f"\n[{i}/{len(articles_to_process)}] Processing: {article['title']} (ID: {article['id']})")
        
        try:
            result = process_article_external_links(article)
            stats['processed'] += 1
            
            if result['success']:
                external_links = result.get('external_links', [])
                
                if update_article_external_links(article['slug'], external_links):
                    stats['success'] += 1
                    stats['total_links_added'] += len(external_links)
                    logger.info(f"[SUCCESS] Added {len(external_links)} external links to '{article['title']}'")
                else:
                    stats['failed'] += 1
                    logger.error(f"[ERROR] Failed to update DB for '{article['title']}'")
            else:
                stats['failed'] += 1
                logger.error(f"[ERROR] Failed to generate links for '{article['title']}': {result.get('error', 'Unknown error')}")
            
            # Delay between articles to avoid rate limiting
            time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error processing article {article.get('title', 'Unknown')}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            stats['processed'] += 1
            stats['failed'] += 1
    
    logger.info("\n" + "=" * 60)
    logger.info("EXTERNAL LINKS GENERATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total articles processed: {stats['processed']}")
    logger.info(f"Successfully updated: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Total external links added: {stats['total_links_added']}")
    logger.info("=" * 60)
    
    if stats['failed'] > 0:
        logger.error("External links generation completed with errors.")
        sys.exit(1)
    else:
        logger.info("External links generation completed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()

