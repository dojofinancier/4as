#!/usr/bin/env python3
"""
Direct outline generation - processes articles and generates SQL updates.
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
        logging.FileHandler('outline_gen.log'),
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

# Articles from first batch
articles = [
    {"id": "eae811d9-112d-4b1f-a224-e87f1077f41a", "slug": "comprendre-facilement-le-sommeil-etudiant", "title": "Comprendre facilement le sommeil étudiant", "category": "Méthodes d'étude & productivité"},
    {"id": "bfac3876-55f8-45a3-a361-be9ba9ed5efc", "slug": "optimiser-sa-reussite-en-la-lecture-academique", "title": "Optimiser sa réussite en la lecture académique", "category": "Orientation universitaire & carrière"},
    {"id": "a4733c8d-afc9-4bc9-a22d-871340a27da7", "slug": "approche-pratique-de-les-presentations-orales", "title": "Approche pratique de les présentations orales", "category": "Vie universitaire & bien-être"},
    {"id": "a51e9d8d-2c65-4bc6-aed1-f3c32884f733", "slug": "techniques-modernes-pour-etudier-lanalyse-financiere", "title": "Techniques modernes pour étudier l'analyse financière", "category": "Réussite aux examens"},
    {"id": "b0d6c6e6-d7b5-439c-bb43-885b2d122ee9", "slug": "approche-pratique-de-la-concentration", "title": "Approche pratique de la concentration", "category": "Conseils par matières"},
    {"id": "a7b5f4a1-ab75-4698-a9e4-e6ef2bee7c05", "slug": "secrets-pour-reussir-en-la-microeconomie", "title": "Secrets pour réussir en la microéconomie", "category": "Outils & technologie"},
    {"id": "93b35ddd-8a15-4e7f-86f2-40657d46292f", "slug": "methode-simple-pour-apprendre-la-methodologie-universitaire", "title": "Méthode simple pour apprendre la méthodologie universitaire", "category": "Conseils par matières"},
    {"id": "fc91e00e-df52-4cfa-986b-e4fd58ba8558", "slug": "methode-simple-pour-apprendre-lorganisation-personnelle", "title": "Méthode simple pour apprendre l'organisation personnelle", "category": "Réussite aux examens"},
    {"id": "f4e49875-077d-43e7-bcc4-280b6e883405", "slug": "comment-maitriser-les-presentations-orales", "title": "Comment maîtriser les présentations orales", "category": "Méthodes d'étude & productivité"},
    {"id": "c4e7e2cc-7448-4c1a-91ae-eb98addf395e", "slug": "introduction-pratique-a-les-statistiques", "title": "Introduction pratique à les statistiques", "category": "Travaux, présentations & études de cas"}
]

if __name__ == '__main__':
    results = []
    sql_updates = []
    
    for i, article in enumerate(articles, 1):
        logger.info(f"Processing {i}/{len(articles)}: {article['title']}")
        result = generate_outline(article['title'], article['category'])
        
        if result['success']:
            outline_escaped = result['outline'].replace("'", "''")
            sql = f"UPDATE general_articles SET draft_outline = '{outline_escaped}', status = 'draft', updated_at = NOW() WHERE slug = '{article['slug']}';"
            sql_updates.append(sql)
            results.append({'slug': article['slug'], 'success': True})
            logger.info(f"✓ Generated outline for: {article['title']}")
        else:
            results.append({'slug': article['slug'], 'success': False, 'error': result.get('error')})
            logger.error(f"✗ Failed: {article['title']} - {result.get('error')}")
        
        time.sleep(1)  # Rate limiting
    
    # Save SQL
    with open('scripts/articles/batch_1_outlines.sql', 'w', encoding='utf-8') as f:
        f.write("-- Outline generation batch 1\n\n")
        for sql in sql_updates:
            f.write(sql + "\n\n")
    
    # Save results
    with open('scripts/articles/batch_1_outlines_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Batch 1 Complete: {sum(1 for r in results if r.get('success'))}/{len(results)} successful")
    logger.info(f"SQL saved to: scripts/articles/batch_1_outlines.sql")

