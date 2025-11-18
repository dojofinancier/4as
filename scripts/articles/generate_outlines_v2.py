#!/usr/bin/env python3
"""
Generate article outlines using improved prompts from article_prompts.md

This script:
1. Fetches articles with status='draft_outline' and no draft_outline yet
2. Generates outlines using the first prompt from article_prompts.md
3. Optionally improves outlines using the second prompt
4. Updates database with generated outlines
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
        logging.FileHandler('outline_generation.log'),
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

def load_prompt_from_file() -> str:
    """Load the outline generation prompt from article_prompts.md"""
    prompt_file = os.path.join(os.path.dirname(__file__), 'article_prompts.md')
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the first prompt (PROMPT TO GENERATE OUTLINE)
        # Find the section between "#PROMPT TO GENERATE OUTLINE" and "# PROMPT TO IMPROVE OUTLINE"
        start_marker = "#PROMPT TO GENERATE OUTLINE"
        end_marker = "# PROMPT TO IMPROVE OUTLINE"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx == -1:
            logger.error("Could not find prompt start marker in article_prompts.md")
            return None
        
        if end_idx == -1:
            # Use rest of file if no end marker
            prompt_text = content[start_idx + len(start_marker):].strip()
        else:
            prompt_text = content[start_idx + len(start_marker):end_idx].strip()
        
        return prompt_text
    
    except Exception as e:
        logger.error(f"Error loading prompt from file: {e}")
        return None

def load_improve_prompt_from_file() -> str:
    """Load the outline improvement prompt from article_prompts.md"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_file = os.path.join(script_dir, 'article_prompts.md')
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the second prompt (PROMPT TO IMPROVE OUTLINE)
        start_marker = "# PROMPT TO IMPROVE OUTLINE"
        end_marker = "# PROMPT TO DRAFT THE ARTICLE"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx == -1:
            logger.error("Could not find improve prompt start marker in article_prompts.md")
            return None
        
        if end_idx == -1:
            prompt_text = content[start_idx + len(start_marker):].strip()
        else:
            prompt_text = content[start_idx + len(start_marker):end_idx].strip()
        
        return prompt_text
    
    except Exception as e:
        logger.error(f"Error loading improve prompt from file: {e}")
        return None

def build_outline_prompt(title: str, category: str, base_prompt: str) -> str:
    """Build the AI prompt for outline generation by replacing placeholders."""
    # Replace {{ARTICLE_TITLE}} with actual title
    prompt = base_prompt.replace('{{ARTICLE_TITLE}}', title)
    
    # Generate article goal from title/category if needed
    # For now, we'll use a simple goal based on the title
    article_goal = f"Créer un guide pratique et détaillé pour aider les étudiants en gestion à {title.lower()}"
    prompt = prompt.replace('{{ARTICLE_GOAL}}', article_goal)
    
    # Add instruction about avoiding geographical references
    additional_instruction = """

**IMPORTANT - Style note:**
- Ne pas inclure de références géographiques explicites comme "(les étudiants du Québec)", "(au Québec)", etc. dans les titres ou le contenu
- Le contexte géographique est déjà assumé et ces références sonnent peu naturelles
- Écrire comme si on s'adresse directement aux étudiants sans mentionner leur localisation"""
    
    # Add this instruction before the final "Now, using all of the instructions above..."
    if "Now, using all of the instructions above" in prompt:
        prompt = prompt.replace(
            "Now, using all of the instructions above",
            additional_instruction + "\n\nNow, using all of the instructions above"
        )
    else:
        # If the pattern isn't found, append at the end
        prompt += additional_instruction
    
    return prompt

def build_improve_prompt(outline: str, base_prompt: str) -> str:
    """Build the AI prompt for outline improvement by replacing placeholders."""
    prompt = base_prompt.replace('{{OUTLINE_HERE}}', outline)
    return prompt

def generate_outline(title: str, category: str, base_prompt: str) -> Dict[str, any]:
    """Generate article outline using OpenAI API with gpt-5-nano."""
    prompt = build_outline_prompt(title, category, base_prompt)
    
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en stratégie de contenu et tuteur universitaire qui aide les étudiants de premier cycle en gestion du Québec à réussir leurs études."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=2000,
            reasoning_effort="minimal",
            verbosity="medium"
        )
        
        if not response.choices or len(response.choices) == 0:
            logger.error(f"No choices in response for {title}")
            return {
                'success': False,
                'error': 'No response choices'
            }
        
        outline = response.choices[0].message.content
        
        if not outline:
            logger.error(f"Empty outline in response for {title}")
            return {
                'success': False,
                'error': 'Empty outline in response'
            }
        
        logger.info(f"Generated outline length: {len(outline)} chars for {title[:50]}...")
        
        return {
            'outline': outline,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error generating outline for {title}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def improve_outline(outline: str, base_prompt: str) -> Dict[str, any]:
    """Improve outline using OpenAI API with gpt-5-nano."""
    prompt = build_improve_prompt(outline, base_prompt)
    
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en stratégie de contenu et tuteur universitaire qui aide les étudiants de premier cycle en gestion du Québec à réussir leurs études."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=2000,
            reasoning_effort="minimal",
            verbosity="medium"
        )
        
        if not response.choices or len(response.choices) == 0:
            logger.error("No choices in response for outline improvement")
            return {
                'success': False,
                'error': 'No response choices'
            }
        
        improved_outline = response.choices[0].message.content
        
        if not improved_outline:
            logger.error("Empty improved outline in response")
            return {
                'success': False,
                'error': 'Empty improved outline in response'
            }
        
        logger.info(f"Improved outline length: {len(improved_outline)} chars")
        
        return {
            'outline': improved_outline,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error improving outline: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def validate_outline(outline: str) -> Tuple[bool, str]:
    """Validate outline structure."""
    # Check for H1 (supports both markdown "#" and "H1 :" formats)
    h1_markdown = len(re.findall(r'^#\s+', outline, re.MULTILINE))
    h1_text = len(re.findall(r'^H1\s*:', outline, re.MULTILINE | re.IGNORECASE))
    h1_count = h1_markdown + h1_text
    
    if h1_count != 1:
        return False, f"Expected 1 H1, found {h1_count} (markdown: {h1_markdown}, text: {h1_text})"
    
    # Check for H2 sections (should be 8-12) - supports both formats
    h2_markdown = len(re.findall(r'^##\s+', outline, re.MULTILINE))
    h2_text = len(re.findall(r'^H2\s*:', outline, re.MULTILINE | re.IGNORECASE))
    h2_count = h2_markdown + h2_text
    
    if h2_count < 8 or h2_count > 12:
        return False, f"Expected 8-12 H2 sections, found {h2_count} (markdown: {h2_markdown}, text: {h2_text})"
    
    # Check for required sections
    required_sections = [
        "Erreurs fréquentes",
        "Astuces de tuteur",
        "Mini-checklist"
    ]
    outline_lower = outline.lower()
    for section in required_sections:
        if section.lower() not in outline_lower:
            return False, f"Missing required section: {section}"
    
    # Check for H3 subsections (at least some) - supports both formats
    h3_markdown = len(re.findall(r'^###\s+', outline, re.MULTILINE))
    h3_text = len(re.findall(r'^H3\s*:', outline, re.MULTILINE | re.IGNORECASE))
    h3_count = h3_markdown + h3_text
    
    if h3_count < h2_count:  # Should have at least 1 H3 per H2
        return False, f"Not enough H3 subsections: found {h3_count} for {h2_count} H2s"
    
    return True, "Valid"

def fetch_articles_needing_outlines(limit: int = None) -> List[Dict]:
    """Fetch articles that need outlines."""
    try:
        query = supabase.from_('general_articles')\
            .select('id, slug, title, category')\
            .eq('status', 'draft_outline')\
            .is_('draft_outline', 'null')
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} articles needing outlines")
            return response.data
        else:
            logger.info("No articles found needing outlines")
            return []
    
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []

def update_article_outline(slug: str, outline: str) -> bool:
    """Update article with generated outline."""
    try:
        update_data = {
            'draft_outline': outline,
            'status': 'draft',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase.from_('general_articles')\
            .update(update_data)\
            .eq('slug', slug)\
            .execute()
        
        if result.data:
            logger.info(f"Updated outline for article: {slug}")
            return True
        else:
            logger.error(f"Failed to update outline for article: {slug}")
            return False
    
    except Exception as e:
        logger.error(f"Error updating article outline for {slug}: {e}")
        return False

def main():
    """Main function."""
    logger.info("=" * 60)
    logger.info("OUTLINE GENERATION - ALL REMAINING ARTICLES")
    logger.info("=" * 60)
    
    # Load prompts
    logger.info("Loading prompts from article_prompts.md...")
    base_prompt = load_prompt_from_file()
    improve_prompt = load_improve_prompt_from_file()
    
    if not base_prompt:
        logger.error("Failed to load base prompt")
        sys.exit(1)
    
    if not improve_prompt:
        logger.warning("Failed to load improve prompt - will skip improvement step")
    
    # Fetch all articles needing outlines
    logger.info("Fetching articles needing outlines...")
    articles = fetch_articles_needing_outlines(limit=None)  # None = fetch all
    
    if not articles:
        logger.info("No articles found needing outlines")
        sys.exit(0)
    
    logger.info(f"Processing {len(articles)} articles...")
    
    # Process articles
    stats = {
        'processed': 0,
        'success': 0,
        'failed': 0,
        'improved': 0
    }
    
    for i, article in enumerate(articles, 1):
        logger.info(f"\n[{i}/{len(articles)}] Processing: {article['title']}")
        
        try:
            # Generate initial outline
            logger.info("Generating initial outline...")
            result = generate_outline(
                article['title'],
                article['category'],
                base_prompt
            )
            
            if not result['success']:
                logger.error(f"Failed to generate outline: {result.get('error')}")
                stats['failed'] += 1
                continue
            
            outline = result['outline']
            
            # Optionally improve outline
            if improve_prompt:
                logger.info("Improving outline...")
                improve_result = improve_outline(outline, improve_prompt)
                
                if improve_result['success']:
                    outline = improve_result['outline']
                    stats['improved'] += 1
                    logger.info("Outline improved successfully")
                else:
                    logger.warning(f"Failed to improve outline, using original: {improve_result.get('error')}")
            
            # Validate outline
            is_valid, validation_msg = validate_outline(outline)
            if not is_valid:
                logger.warning(f"Outline validation warning: {validation_msg}")
                logger.info("Continuing anyway...")
            
            # Update database
            if update_article_outline(article['slug'], outline):
                stats['success'] += 1
                logger.info(f"[SUCCESS] Successfully processed: {article['title']}")
            else:
                stats['failed'] += 1
                logger.error(f"[FAILED] Failed to update database: {article['title']}")
            
            stats['processed'] += 1
            
            # Small delay between articles to avoid rate limiting
            if i < len(articles):
                time.sleep(1.5)  # Slightly longer delay for larger batches
        
        except Exception as e:
            logger.error(f"Error processing article {article['title']}: {e}")
            stats['failed'] += 1
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("BATCH SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total processed: {stats['processed']}")
    logger.info(f"Successful: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Improved: {stats['improved']}")
    logger.info("=" * 60)
    
    if stats['failed'] > 0:
        logger.warning(f"Completed with {stats['failed']} failures")
        sys.exit(1)
    else:
        logger.info("Batch completed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()

