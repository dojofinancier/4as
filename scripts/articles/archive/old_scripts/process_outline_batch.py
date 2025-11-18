#!/usr/bin/env python3
"""
Process outline generation for a batch of articles.
This script generates outlines and prepares SQL updates.
"""

import os
import sys
import json
import logging
from typing import Dict, List
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('article_outline_generation.log'),
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

def build_outline_prompt(title: str, category: str) -> str:
    """Build the AI prompt for outline generation."""
    prompt = f"""Tu es un expert en rédaction de contenu éducatif en français. Génère un plan détaillé (outline) pour un article de blog de 1000-2000 mots sur le sujet suivant.

**Titre de l'article:** {title}
**Catégorie:** {category}

**Instructions:**
- Le plan doit être structuré et détaillé
- Utilise des titres de sections (h2) et sous-sections (h3)
- Chaque section doit avoir une description de 2-3 phrases expliquant ce qui sera couvert
- Le plan doit couvrir suffisamment de contenu pour un article de 1000-2000 mots
- Le contenu doit être en français
- Le plan doit être en format markdown

**Structure suggérée:**
- Introduction (2-3 paragraphes)
- Sections principales avec sous-sections (4-6 sections principales)
- Conclusion (1-2 paragraphes)

Génère maintenant le plan détaillé en markdown."""
    
    return prompt

def generate_outline(title: str, category: str) -> Dict[str, any]:
    """Generate article outline using OpenAI API."""
    prompt = build_outline_prompt(title, category)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en rédaction de contenu éducatif en français. Tu génères des plans détaillés et structurés pour des articles de blog."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        if not response.choices or len(response.choices) == 0:
            return {
                'success': False,
                'error': 'No response choices'
            }
        
        outline = response.choices[0].message.content
        
        if not outline:
            return {
                'success': False,
                'error': 'Empty outline in response'
            }
        
        logger.info(f"Generated outline: {len(outline)} chars for {title}")
        
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

# Articles to process (will be provided by assistant via MCP)
articles = []

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python process_outline_batch.py <articles_json>")
        print("Articles JSON should be an array of {id, slug, title, category}")
        sys.exit(1)
    
    # Parse articles from JSON argument
    try:
        articles = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Error: Invalid JSON provided")
        sys.exit(1)
    
    results = []
    sql_updates = []
    
    for i, article in enumerate(articles, 1):
        logger.info(f"Processing {i}/{len(articles)}: {article['title']}")
        
        result = generate_outline(article['title'], article['category'])
        
        if result['success']:
            # Escape single quotes for SQL
            outline_escaped = result['outline'].replace("'", "''")
            
            sql = f"""
UPDATE general_articles 
SET draft_outline = '{outline_escaped}',
    status = 'draft',
    updated_at = NOW()
WHERE slug = '{article['slug']}';
"""
            sql_updates.append(sql.strip())
            results.append({
                'slug': article['slug'],
                'success': True
            })
        else:
            results.append({
                'slug': article['slug'],
                'success': False,
                'error': result.get('error', 'Unknown error')
            })
        
        # Small delay to avoid rate limiting
        time.sleep(1)
    
    # Save SQL updates
    sql_file = 'scripts/articles/outline_batch_updates.sql'
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- Outline generation batch updates\n")
        f.write(f"-- Generated: {len(articles)} articles\n\n")
        for sql in sql_updates:
            f.write(sql + "\n\n")
    
    # Save results
    results_file = 'scripts/articles/outline_batch_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Processed {len(articles)} articles")
    logger.info(f"SQL updates saved to: {sql_file}")
    logger.info(f"Results saved to: {results_file}")
    logger.info(f"Success: {sum(1 for r in results if r.get('success'))}/{len(results)}")

