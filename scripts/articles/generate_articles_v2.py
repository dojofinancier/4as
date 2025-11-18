#!/usr/bin/env python3
"""
Generate full articles from outlines using improved prompts from article_prompts.md

This script:
1. Fetches articles with status='draft' and draft_outline populated but no content
2. Generates articles using the third prompt from article_prompts.md
3. Optionally improves articles using the fourth prompt
4. Updates database with generated content, metadata, tags, keywords
"""

import os
import sys
import re
import logging
import time
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
        logging.FileHandler('article_gen_live.log', encoding='utf-8'),
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

def load_prompt_from_file(prompt_name: str) -> str:
    """Load a specific prompt from article_prompts.md"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_file = os.path.join(script_dir, 'article_prompts.md')
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Map prompt names to markers
        markers = {
            'draft': ('# PROMPT TO DRAFT THE ARTICLE', '# PROMPT TO IMPROVE THE DRAFT ARTICLE'),
            'improve': ('# PROMPT TO IMPROVE THE DRAFT ARTICLE', None)
        }
        
        if prompt_name not in markers:
            logger.error(f"Unknown prompt name: {prompt_name}")
            return None
        
        start_marker, end_marker = markers[prompt_name]
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            logger.error(f"Could not find prompt start marker: {start_marker}")
            return None
        
        if end_marker:
            end_idx = content.find(end_marker, start_idx + len(start_marker))
            if end_idx == -1:
                logger.warning(f"Could not find end marker, using rest of file")
                prompt_text = content[start_idx + len(start_marker):].strip()
            else:
                prompt_text = content[start_idx + len(start_marker):end_idx].strip()
        else:
            # For last prompt, use rest of file
            prompt_text = content[start_idx + len(start_marker):].strip()
        
        return prompt_text
    
    except Exception as e:
        logger.error(f"Error loading prompt from file: {e}")
        return None

def build_article_prompt(title: str, category: str, outline: str, base_prompt: str) -> str:
    """Build the AI prompt for article generation by replacing placeholders."""
    # Replace placeholders
    prompt = base_prompt.replace('{{ARTICLE_TITLE}}', title)
    prompt = prompt.replace('{{OUTLINE_HERE}}', outline)
    
    # Add instruction about avoiding geographical references - CRITICAL
    additional_instruction = """

**⚠️ RÈGLE ABSOLUE - INTERDICTION STRICTE ⚠️**
- NE JAMAIS mentionner "Québec", "au Québec", "du Québec", "pour les étudiants du Québec", "(les étudiants du Québec)", "étudiants en gestion au Québec", ou toute autre référence géographique dans le contenu
- Le contexte géographique est déjà assumé par le public cible - ces références sont inutiles et sonnent peu naturelles
- Si tu inclus une référence géographique, le contenu sera IMMÉDIATEMENT REJETÉ
- Écris comme si tu t'adresses directement aux étudiants sans mentionner leur localisation
- Commence directement par "Tu es étudiant en gestion" ou "Tu es en gestion" - SANS mentionner le Québec
- Exemple INTERDIT: "Tu es étudiant en gestion au Québec"
- Exemple CORRECT: "Tu es étudiant en gestion" ou "Tu es en gestion" """
    
    # Add this instruction before the final section
    if "Here is the title and the outline to use" in prompt:
        prompt = prompt.replace(
            "Here is the title and the outline to use",
            additional_instruction + "\n\nHere is the title and the outline to use"
        )
    else:
        # If the pattern isn't found, append at the end
        prompt += additional_instruction
    
    return prompt

def build_improve_prompt(article: str, base_prompt: str) -> str:
    """Build the AI prompt for article improvement by replacing placeholders."""
    prompt = base_prompt.replace('{{ARTICLE_DRAFT}}', article)
    
    # Add instruction about avoiding geographical references - CRITICAL
    additional_instruction = """

**⚠️ RÈGLE ABSOLUE - INTERDICTION STRICTE ⚠️**
- NE JAMAIS mentionner "Québec", "au Québec", "du Québec", "pour les étudiants du Québec", "(les étudiants du Québec)", "étudiants en gestion au Québec", ou toute autre référence géographique dans le contenu
- Si le contenu actuel contient des références géographiques, SUPPRIME-LES COMPLÈTEMENT lors de l'amélioration
- Le contexte géographique est déjà assumé par le public cible - ces références sont inutiles et sonnent peu naturelles
- Si tu inclus une référence géographique, le contenu sera IMMÉDIATEMENT REJETÉ
- Écris comme si tu t'adresses directement aux étudiants sans mentionner leur localisation"""
    
    # Append the instruction at the end
    prompt += additional_instruction
    
    return prompt

def count_words(text: str) -> int:
    """Count words in text (handles markdown)."""
    # Remove markdown syntax for word count
    text = re.sub(r'[#*`\[\]()]', '', text)
    text = re.sub(r'\n+', ' ', text)
    words = text.split()
    return len(words)

def generate_article(title: str, category: str, outline: str, base_prompt: str, max_retries: int = 2) -> Dict[str, any]:
    """Generate full article using OpenAI API with gpt-5-nano."""
    prompt = build_article_prompt(title, category, outline, base_prompt)
    
    # Log prompt length for debugging
    prompt_length = len(prompt)
    outline_length = len(outline)
    logger.info(f"Prompt length: {prompt_length} chars (outline: {outline_length} chars) for {title[:50]}...")
    
    if prompt_length > 100000:  # Very long prompts might cause issues
        logger.warning(f"Prompt is very long ({prompt_length} chars), might cause issues")
        logger.warning(f"Consider truncating outline if it's too long")
    
    # Retry logic for empty responses
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries} for {title[:50]}...")
                time.sleep(2)  # Wait before retry
            
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en stratégie de contenu et tuteur universitaire qui aide les étudiants de premier cycle en gestion à réussir leurs études. RÈGLE ABSOLUE: Ne jamais mentionner 'Québec', 'au Québec', 'du Québec', ou toute référence géographique dans le contenu généré. Le contexte géographique est assumé et ne doit pas être mentionné explicitement."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=50000,  # GPT-5-nano supports up to 128k output tokens. Set high to allow reasoning + content (2000 words ≈ 2667 tokens, but reasoning needs headroom)
                reasoning_effort="high",  # HIGH reasoning for better quality and adherence to instructions
                verbosity="medium"  # Medium verbosity balances quality and token usage
            )
            
            if not response.choices or len(response.choices) == 0:
                if attempt < max_retries:
                    logger.warning(f"No choices in response (attempt {attempt + 1}), retrying...")
                    continue  # Retry
                else:
                    logger.error(f"No choices in response for {title}")
                    return {
                        'success': False,
                        'error': 'No response choices'
                    }
            
            choice = response.choices[0]
            
            # Check finish reason
            if hasattr(choice, 'finish_reason') and choice.finish_reason != 'stop':
                logger.warning(f"Article generation finished with reason: {choice.finish_reason} for {title}")
                if choice.finish_reason == 'length':
                    logger.warning("Response was truncated due to length limit - will retry with higher limit")
                    if attempt < max_retries:
                        # Increase max_completion_tokens on retry
                        continue  # Retry with same settings (will use higher limit if we modify)
                    else:
                        logger.error("Response truncated after all retries - content may be incomplete")
            
            # Check if content exists - might be in different fields for gpt-5-nano
            article_content = None
            if hasattr(choice.message, 'content'):
                article_content = choice.message.content
            
            # For gpt-5-nano, check if there's reasoning content that needs to be extracted
            if not article_content or not article_content.strip():
                # Check if there's a reasoning field or other content fields
                if hasattr(choice.message, 'reasoning_content'):
                    article_content = choice.message.reasoning_content
                    logger.info("Found content in reasoning_content field")
                elif hasattr(choice, 'message') and hasattr(choice.message, 'refusal'):
                    logger.warning("Model refused to generate content")
                elif hasattr(response, 'choices') and len(response.choices) > 0:
                    # Try to get any text content from the response
                    logger.warning("No content found in standard fields, checking response structure")
            
            # Check for empty or None content
            if not article_content or not article_content.strip():
                if attempt < max_retries:
                    logger.warning(f"Empty article in response (attempt {attempt + 1}), retrying...")
                    continue  # Retry
                else:
                    logger.error(f"Empty article in response for {title} after {max_retries + 1} attempts")
                    logger.error(f"Response content type: {type(article_content)}")
                    logger.error(f"Response content length: {len(article_content) if article_content else 0}")
                    logger.error(f"Finish reason: {getattr(choice, 'finish_reason', 'unknown')}")
                    logger.error(f"Response ID: {response.id if hasattr(response, 'id') else 'unknown'}")
                    logger.error(f"Usage: {response.usage if hasattr(response, 'usage') else 'unknown'}")
                    # Log first 500 chars of prompt for debugging
                    logger.error(f"Prompt preview (first 500 chars): {prompt[:500]}...")
                    logger.error(f"Prompt total length: {len(prompt)}")
                    logger.error(f"Outline length: {len(outline)}")
                    return {
                        'success': False,
                        'error': 'Empty article in response after retries'
                    }
            
            # Success - we got content
            word_count = count_words(article_content)
            
            # Log token usage for successful generation
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                completion_tokens = getattr(usage, 'completion_tokens', 0)
                total_tokens = getattr(usage, 'total_tokens', 0)
                reasoning_tokens = 0
                if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details:
                    reasoning_tokens = getattr(usage.completion_tokens_details, 'reasoning_tokens', 0)
                
                logger.info(f"Generated article: {word_count} words for {title[:50]}...")
                logger.info(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens} (Reasoning: {reasoning_tokens}), Total: {total_tokens}")
            else:
                logger.info(f"Generated article: {word_count} words for {title[:50]}...")
            
            return {
                'content': article_content,
                'word_count': word_count,
                'success': True
            }
        
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Error generating article (attempt {attempt + 1}): {e}, retrying...")
                continue  # Retry
            else:
                logger.error(f"Error generating article for {title} after {max_retries + 1} attempts: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
    
    # Should not reach here, but just in case
    return {
        'success': False,
        'error': 'Failed after all retry attempts'
    }

def improve_article(article: str, base_prompt: str) -> Dict[str, any]:
    """Improve article using OpenAI API with gpt-5-nano."""
    prompt = build_improve_prompt(article, base_prompt)
    
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en stratégie de contenu et tuteur universitaire qui aide les étudiants de premier cycle en gestion à réussir leurs études. RÈGLE ABSOLUE: Ne jamais mentionner 'Québec', 'au Québec', 'du Québec', ou toute référence géographique dans le contenu généré. Le contexte géographique est assumé et ne doit pas être mentionné explicitement."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=50000,  # GPT-5-nano supports up to 128k output tokens. Set high to allow reasoning + content
            reasoning_effort="high",  # HIGH reasoning for better quality and adherence to instructions
            verbosity="medium"  # Medium verbosity balances quality and token usage
        )
        
        if not response.choices or len(response.choices) == 0:
            logger.error("No choices in response for article improvement")
            return {
                'success': False,
                'error': 'No response choices'
            }
        
        choice = response.choices[0]
        
        # Check finish reason
        if hasattr(choice, 'finish_reason') and choice.finish_reason != 'stop':
            logger.warning(f"Article improvement finished with reason: {choice.finish_reason}")
            if choice.finish_reason == 'length':
                logger.warning("Response was truncated due to length limit")
        
        improved_article = choice.message.content
        
        # Check for empty or None content
        if not improved_article or not improved_article.strip():
            logger.error("Empty improved article in response")
            logger.error(f"Response content type: {type(improved_article)}")
            logger.error(f"Response content length: {len(improved_article) if improved_article else 0}")
            return {
                'success': False,
                'error': 'Empty improved article in response'
            }
        
        word_count = count_words(improved_article)
        
        # Log token usage for successful improvement
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
            completion_tokens = getattr(usage, 'completion_tokens', 0)
            total_tokens = getattr(usage, 'total_tokens', 0)
            reasoning_tokens = 0
            if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details:
                reasoning_tokens = getattr(usage.completion_tokens_details, 'reasoning_tokens', 0)
            
            logger.info(f"Improved article: {word_count} words")
            logger.info(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens} (Reasoning: {reasoning_tokens}), Total: {total_tokens}")
        else:
            logger.info(f"Improved article: {word_count} words")
        
        return {
            'content': improved_article,
            'word_count': word_count,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error improving article: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def extract_metadata(article_content: str, title: str) -> Dict[str, any]:
    """Extract metadata from article content."""
    # Extract H1 (first heading in content)
    h1_match = re.search(r'^#\s+(.+)$', article_content, re.MULTILINE)
    h1 = h1_match.group(1).strip() if h1_match else title
    
    # Generate meta description (first 150 chars of content, cleaned)
    content_clean = re.sub(r'[#*`\[\]()]', '', article_content)
    meta_desc = content_clean[:150].strip()
    if len(meta_desc) == 150:
        meta_desc += "..."
    
    # Generate excerpt (first 200 chars)
    excerpt = content_clean[:200].strip()
    if len(excerpt) == 200:
        excerpt += "..."
    
    # Count words
    word_count = count_words(article_content)
    
    # Extract tags and keywords (if provided in special format)
    # For now, we'll generate empty arrays - can be enhanced later
    tags = []
    keywords = []
    
    return {
        'h1': h1,
        'meta_description': meta_desc,
        'excerpt': excerpt,
        'word_count': word_count,
        'tags': tags,
        'keywords': keywords
    }

def validate_article(article_content: str, metadata: Dict) -> Tuple[bool, str]:
    """Validate article quality."""
    # Check word count (should be 1500-2000, but allow flexibility - no upper limit)
    word_count = metadata['word_count']
    if word_count < 1000:
        return False, f"Article too short: {word_count} words (expected at least 1000)"
    # Removed upper limit - allow longer articles
    
    # Check for H1
    h1_count = len(re.findall(r'^#\s+', article_content, re.MULTILINE))
    if h1_count == 0:
        return False, "No H1 heading found"
    
    # Check for H2 sections (should have some structure, but be lenient)
    h2_count = len(re.findall(r'^##\s+', article_content, re.MULTILINE))
    if h2_count < 3:
        return False, f"Not enough H2 sections: {h2_count} (expected at least 3)"
    
    return True, "Valid"

def fetch_articles_ready_for_generation(limit: int = None) -> List[Dict]:
    """Fetch articles that need content generation."""
    try:
        query = supabase.from_('general_articles')\
            .select('id, slug, title, category, draft_outline')\
            .eq('status', 'draft')\
            .not_.is_('draft_outline', 'null')\
            .is_('content', 'null')
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} articles ready for generation")
            return response.data
        else:
            logger.info("No articles found ready for generation")
            return []
    
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []

def update_article_content(slug: str, article_content: str, metadata: Dict) -> bool:
    """Update article with generated content and metadata."""
    try:
        update_data = {
            'content': article_content,
            'h1': metadata['h1'],
            'meta_description': metadata['meta_description'],
            'excerpt': metadata['excerpt'],
            'tags': metadata['tags'],
            'keywords': metadata['keywords'],
            'word_count': metadata['word_count'],
            'status': 'draft',  # Keep as 'draft' - content_generated is not a valid status
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase.from_('general_articles')\
            .update(update_data)\
            .eq('slug', slug)\
            .execute()
        
        if result.data:
            logger.info(f"Updated content for article: {slug}")
            return True
        else:
            logger.error(f"Failed to update content for article: {slug}")
            return False
    
    except Exception as e:
        logger.error(f"Error updating article content for {slug}: {e}")
        return False

def main():
    """Main function."""
    logger.info("=" * 60)
    logger.info("ARTICLE GENERATION - ALL ARTICLES")
    logger.info("=" * 60)
    
    # Load prompts
    logger.info("Loading prompts from article_prompts.md...")
    draft_prompt = load_prompt_from_file('draft')
    improve_prompt = load_prompt_from_file('improve')
    
    if not draft_prompt:
        logger.error("Failed to load draft prompt")
        sys.exit(1)
    
    if not improve_prompt:
        logger.warning("Failed to load improve prompt - will skip improvement step")
    
    # Fetch articles
    logger.info("Fetching articles ready for generation...")
    articles = fetch_articles_ready_for_generation(limit=None)  # None = fetch all
    
    if not articles:
        logger.info("No articles found ready for generation")
        sys.exit(0)
    
    logger.info(f"Processing {len(articles)} articles...")
    
    # Process articles
    stats = {
        'processed': 0,
        'success': 0,
        'failed': 0,
        'improved': 0,
        'total_words': 0
    }
    
    for i, article in enumerate(articles, 1):
        logger.info(f"\n[{i}/{len(articles)}] Processing: {article['title']}")
        
        try:
            if not article.get('draft_outline'):
                logger.error(f"ERROR: No outline found for article: {article['title']}")
                logger.error(f"Stopping execution. Fix the issue and re-run the script.")
                logger.error(f"Article slug: {article.get('slug', 'unknown')}")
                sys.exit(1)
            
            # Generate initial article
            logger.info("Generating initial article...")
            result = generate_article(
                article['title'],
                article['category'],
                article['draft_outline'],
                draft_prompt
            )
            
            if not result['success']:
                logger.error(f"ERROR: Failed to generate article: {result.get('error')}")
                logger.error(f"Article: {article['title']}")
                logger.error(f"Article slug: {article.get('slug', 'unknown')}")
                
                # Save error details to file for review
                error_file = f"failed_generation_{article.get('slug', 'unknown')}.txt"
                try:
                    with open(error_file, 'w', encoding='utf-8') as f:
                        f.write(f"Article: {article['title']}\n")
                        f.write(f"Slug: {article.get('slug', 'unknown')}\n")
                        f.write(f"Category: {article.get('category', 'Unknown')}\n")
                        f.write(f"Error: {result.get('error')}\n")
                        f.write(f"\nOutline:\n{article.get('draft_outline', 'N/A')}\n")
                    logger.error(f"Error details saved to: {error_file}")
                except Exception as e:
                    logger.error(f"Could not save error details: {e}")
                
                logger.error(f"Stopping execution. Fix the issue and re-run the script.")
                sys.exit(1)
            
            article_content = result['content']
            
            # Optionally improve article
            if improve_prompt:
                logger.info("Improving article...")
                improve_result = improve_article(article_content, improve_prompt)
                
                if improve_result['success']:
                    article_content = improve_result['content']
                    stats['improved'] += 1
                    logger.info("Article improved successfully")
                else:
                    logger.error(f"ERROR: Failed to improve article: {improve_result.get('error')}")
                    logger.error(f"Article: {article['title']}")
                    logger.error(f"Article slug: {article.get('slug', 'unknown')}")
                    
                    # Save article before improvement failure for review
                    failed_improve_file = f"failed_improve_{article.get('slug', 'unknown')}.md"
                    try:
                        with open(failed_improve_file, 'w', encoding='utf-8') as f:
                            f.write(f"# {article['title']}\n\n")
                            f.write(f"**Category:** {article.get('category', 'Unknown')}\n\n")
                            f.write(f"**Improvement Error:** {improve_result.get('error')}\n\n")
                            f.write("---\n\n")
                            f.write("**Original Article (before improvement):**\n\n")
                            f.write(article_content)
                        logger.error(f"Article before improvement failure saved to: {failed_improve_file}")
                    except Exception as e:
                        logger.error(f"Could not save article: {e}")
                    
                    logger.error(f"Stopping execution. Fix the issue and re-run the script.")
                    sys.exit(1)
            
            # Extract metadata
            metadata = extract_metadata(article_content, article['title'])
            
            # Validate article
            is_valid, validation_msg = validate_article(article_content, metadata)
            if not is_valid:
                logger.error(f"ERROR: Article validation failed: {validation_msg}")
                logger.error(f"Article: {article['title']}")
                logger.error(f"Article slug: {article.get('slug', 'unknown')}")
                logger.error(f"Word count: {metadata['word_count']}")
                
                # Save failed article to file for review
                failed_article_file = f"failed_article_{article.get('slug', 'unknown')}.md"
                try:
                    with open(failed_article_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {article['title']}\n\n")
                        f.write(f"**Category:** {article.get('category', 'Unknown')}\n\n")
                        f.write(f"**Validation Error:** {validation_msg}\n\n")
                        f.write(f"**Word Count:** {metadata['word_count']}\n\n")
                        f.write("---\n\n")
                        f.write(article_content)
                    logger.error(f"Failed article saved to: {failed_article_file}")
                    logger.error(f"Review the article, fix the validation issue, then re-run the script.")
                except Exception as e:
                    logger.error(f"Could not save failed article to file: {e}")
                
                logger.error(f"Stopping execution. Review the article and fix the issue.")
                sys.exit(1)
            
            # Update database
            if not update_article_content(article['slug'], article_content, metadata):
                logger.error(f"ERROR: Failed to update database for article: {article['title']}")
                logger.error(f"Article slug: {article.get('slug', 'unknown')}")
                
                # Save article that failed to upload to database
                failed_db_file = f"failed_db_upload_{article.get('slug', 'unknown')}.md"
                try:
                    with open(failed_db_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {article['title']}\n\n")
                        f.write(f"**Category:** {article.get('category', 'Unknown')}\n\n")
                        f.write(f"**Word Count:** {metadata['word_count']}\n\n")
                        f.write("---\n\n")
                        f.write(article_content)
                    logger.error(f"Article that failed database upload saved to: {failed_db_file}")
                except Exception as e:
                    logger.error(f"Could not save article: {e}")
                
                logger.error(f"Stopping execution. Fix the database issue and re-run the script.")
                sys.exit(1)
            
            stats['success'] += 1
            stats['total_words'] += metadata['word_count']
            stats['processed'] += 1
            logger.info(f"[SUCCESS] Successfully processed: {article['title']} ({metadata['word_count']} words)")
            
            # Delay between articles to avoid rate limiting
            if i < len(articles):
                time.sleep(2.5)  # Longer delay for larger content
        
        except KeyboardInterrupt:
            logger.info("\nProcess interrupted by user")
            logger.info(f"Processed {stats['processed']} articles successfully before interruption")
            sys.exit(130)  # Standard exit code for Ctrl+C
        
        except Exception as e:
            logger.error(f"ERROR: Unexpected exception processing article {article['title']}: {e}")
            logger.error(f"Stopping execution. Fix the issue and re-run the script.")
            logger.error(f"Article slug: {article.get('slug', 'unknown')}")
            import traceback
            logger.error(traceback.format_exc())
            sys.exit(1)
    
    # Print summary (only reached if all articles processed successfully)
    logger.info("\n" + "=" * 60)
    logger.info("BATCH SUMMARY - ALL ARTICLES PROCESSED SUCCESSFULLY")
    logger.info("=" * 60)
    logger.info(f"Total processed: {stats['processed']}")
    logger.info(f"Successful: {stats['success']}")
    logger.info(f"Improved: {stats['improved']}")
    if stats['success'] > 0:
        avg_words = stats['total_words'] / stats['success']
        logger.info(f"Average word count: {avg_words:.0f} words")
    logger.info("=" * 60)
    logger.info("All articles generated successfully!")
    sys.exit(0)

if __name__ == '__main__':
    main()

