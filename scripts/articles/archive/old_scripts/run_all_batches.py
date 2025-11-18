#!/usr/bin/env python3
"""
Complete automated script to process ALL remaining articles.
Loads articles from JSON and processes them in batches automatically.
"""

import os
import sys
import json
import logging
import time
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/articles/outline_auto_complete.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("Missing OPENAI_API_KEY")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

def build_outline_prompt(title: str, category: str) -> str:
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

def generate_outline(title: str, category: str) -> dict:
    prompt = build_outline_prompt(title, category)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un expert en rédaction de contenu éducatif en français. Tu génères des plans détaillés et structurés pour des articles de blog."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        if not response.choices:
            return {'success': False, 'error': 'No response'}
        outline = response.choices[0].message.content
        if not outline:
            return {'success': False, 'error': 'Empty response'}
        return {'outline': outline, 'success': True}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {'success': False, 'error': str(e)}

def process_batch(articles: list, batch_num: int) -> dict:
    """Process a batch of articles and return SQL updates."""
    results = []
    sql_updates = []
    
    logger.info(f"\n{'='*60}")
    logger.info(f"BATCH {batch_num}: Processing {len(articles)} articles")
    logger.info(f"{'='*60}\n")
    
    for i, article in enumerate(articles, 1):
        logger.info(f"Processing {i}/{len(articles)}: {article['title']}")
        result = generate_outline(article['title'], article['category'])
        
        if result['success']:
            outline = result['outline']
            outline = outline.replace('```markdown', '').replace('```', '').strip()
            outline_escaped = outline.replace("'", "''")
            
            sql = f"UPDATE general_articles SET draft_outline = '{outline_escaped}', status = 'draft', updated_at = NOW() WHERE slug = '{article['slug']}';"
            sql_updates.append(sql)
            results.append({'slug': article['slug'], 'success': True, 'outline_length': len(outline)})
            logger.info(f"Generated outline ({len(outline)} chars)")
        else:
            results.append({'slug': article['slug'], 'success': False, 'error': result.get('error')})
            logger.error(f"Failed: {result.get('error')}")
        
        time.sleep(1)  # Rate limiting
    
    # Save SQL
    sql_file = f'scripts/articles/batch_{batch_num}_outlines.sql'
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(f"-- Outline generation batch {batch_num}\n\n")
        for sql in sql_updates:
            f.write(sql + "\n\n")
    
    # Save results
    results_file = f'scripts/articles/batch_{batch_num}_outlines_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    success_count = sum(1 for r in results if r.get('success'))
    logger.info(f"Batch {batch_num} Complete: {success_count}/{len(results)} successful")
    
    return {'success_count': success_count, 'total': len(results)}

if __name__ == '__main__':
    # Load articles from JSON file (will be created by assistant)
    articles_file = 'scripts/articles/all_remaining_articles.json'
    
    if not os.path.exists(articles_file):
        logger.error(f"Articles file not found: {articles_file}")
        logger.info("The assistant will create this file first")
        sys.exit(1)
    
    with open(articles_file, 'r', encoding='utf-8') as f:
        all_articles = json.load(f)
    
    batch_size = 10
    total_articles = len(all_articles)
    total_batches = (total_articles + batch_size - 1) // batch_size
    
    logger.info(f"\n{'='*60}")
    logger.info(f"PROCESSING ALL REMAINING ARTICLES")
    logger.info(f"Total articles: {total_articles}")
    logger.info(f"Total batches: {total_batches}")
    logger.info(f"Estimated time: {total_batches * 2.5:.1f} minutes")
    logger.info(f"{'='*60}\n")
    
    all_results = []
    start_time = time.time()
    
    for batch_num in range(1, total_batches + 1):
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_articles)
        batch_articles = all_articles[start_idx:end_idx]
        
        result = process_batch(batch_articles, batch_num + 2)  # +2 because batches 1-2 are done
        all_results.append(result)
        
        elapsed = time.time() - start_time
        remaining_batches = total_batches - batch_num
        estimated_remaining = (elapsed / batch_num) * remaining_batches
        
        logger.info(f"Progress: {batch_num}/{total_batches} batches")
        logger.info(f"Elapsed: {elapsed/60:.1f} min | Estimated remaining: {estimated_remaining/60:.1f} min")
        
        if batch_num < total_batches:
            time.sleep(2)  # Small delay between batches
    
    # Final summary
    total_success = sum(r['success_count'] for r in all_results)
    total_processed = sum(r['total'] for r in all_results)
    total_time = time.time() - start_time
    
    logger.info(f"\n{'='*60}")
    logger.info(f"ALL BATCHES COMPLETE!")
    logger.info(f"Total: {total_success}/{total_processed} successful")
    logger.info(f"Total time: {total_time/60:.1f} minutes")
    logger.info(f"{'='*60}")

