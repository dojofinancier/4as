#!/usr/bin/env python3
"""
Run outline generation for articles.
Fetches articles from database and generates outlines in batches.
"""

import os
import sys
import json
import logging
import time
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

def main():
    """Main function - will process articles fetched via MCP."""
    logger.info("=" * 60)
    logger.info("OUTLINE GENERATION - Batch Processing")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This script will be executed by assistant with MCP Supabase access")
    logger.info("The assistant will:")
    logger.info("1. Fetch articles with status='draft_outline'")
    logger.info("2. Process in batches of 10")
    logger.info("3. Generate outlines using OpenAI")
    logger.info("4. Update database with draft_outline and status='draft'")

if __name__ == '__main__':
    main()

