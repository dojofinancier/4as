#!/usr/bin/env python3
"""
Process all remaining articles in batches - generates outlines and updates database.
This script processes articles in batches of 10 and updates the database directly.
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
        logging.FileHandler('scripts/articles/outline_generation_all.log'),
        logging.StreamHandler()
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
            # Clean outline (remove markdown code blocks if present)
            outline = result['outline']
            outline = outline.replace('```markdown', '').replace('```', '').strip()
            outline_escaped = outline.replace("'", "''")
            
            sql = f"UPDATE general_articles SET draft_outline = '{outline_escaped}', status = 'draft', updated_at = NOW() WHERE slug = '{article['slug']}';"
            sql_updates.append(sql)
            results.append({'slug': article['slug'], 'success': True, 'outline_length': len(outline)})
            logger.info(f"✓ Generated outline ({len(outline)} chars) for: {article['title']}")
        else:
            results.append({'slug': article['slug'], 'success': False, 'error': result.get('error')})
            logger.error(f"✗ Failed: {article['title']} - {result.get('error')}")
        
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
    logger.info(f"\n{'='*60}")
    logger.info(f"Batch {batch_num} Complete: {success_count}/{len(results)} successful")
    logger.info(f"SQL saved to: {sql_file}")
    logger.info(f"Results saved to: {results_file}")
    
    return {
        'results': results,
        'sql_updates': sql_updates,
        'success_count': success_count,
        'total': len(results)
    }

# Batch 2 articles
batch_2_articles = [
    {"id": "f9903f8c-f009-4383-bcc6-c8345f9f8f4e", "slug": "strategies-efficaces-pour-progresser-la-reduction-du-stress", "title": "Stratégies efficaces pour progresser la réduction du stress", "category": "Vie universitaire & bien-être"},
    {"id": "a23aa67d-84ae-4121-aa5f-fb56edfe08a8", "slug": "secrets-pour-reussir-en-la-comprehension-des-textes-complexes", "title": "Secrets pour réussir en la compréhension des textes complexes", "category": "Travaux, présentations & études de cas"},
    {"id": "6371c39e-7f41-4f45-81ce-2b5d4185b9ac", "slug": "methode-rapide-pour-lorganisation-personnelle", "title": "Méthode rapide pour l'organisation personnelle", "category": "Outils & technologie"},
    {"id": "86dac23b-83a8-49f8-a862-306a802b544d", "slug": "comment-saméliorer-en-la-resolution-de-problemes", "title": "Comment s'améliorer en la résolution de problèmes", "category": "Méthodes d'étude & productivité"},
    {"id": "0aa752f5-0888-4aac-b827-9f47471c7129", "slug": "comprendre-facilement-la-gestion-du-temps", "title": "Comprendre facilement la gestion du temps", "category": "Réussite aux examens"},
    {"id": "76b33e40-394f-4e0e-a539-2de4204295e3", "slug": "introduction-pratique-a-la-resolution-de-problemes", "title": "Introduction pratique à la résolution de problèmes", "category": "Conseils par matières"},
    {"id": "998539fd-87b5-4172-87ae-1e790414fe0a", "slug": "approche-pratique-de-la-prise-de-notes", "title": "Approche pratique de la prise de notes", "category": "Orientation universitaire & carrière"},
    {"id": "ca9cfc9a-03cd-4c6a-b5b1-63497ba92e10", "slug": "methode-simple-pour-apprendre-la-planification-de-session", "title": "Méthode simple pour apprendre la planification de session", "category": "Vie universitaire & bien-être"},
    {"id": "5615e2b4-01ca-4f9b-a5e8-f3ab9155f7d2", "slug": "approche-pratique-de-le-sommeil-etudiant", "title": "Approche pratique de le sommeil étudiant", "category": "Travaux, présentations & études de cas"},
    {"id": "d4ad352e-485a-46e8-8950-bd546fe62940", "slug": "secrets-pour-reussir-en-la-reduction-du-stress", "title": "Secrets pour réussir en la réduction du stress", "category": "Orientation universitaire & carrière"}
]

if __name__ == '__main__':
    # Process batch 2
    result = process_batch(batch_2_articles, 2)
    logger.info(f"\nBatch 2 processing complete!")
    logger.info(f"Success: {result['success_count']}/{result['total']}")

