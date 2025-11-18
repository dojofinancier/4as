#!/usr/bin/env python3
"""
Step 7: AI Content Generation Script

Generates blog post content using OpenAI API for all courses.
Processes courses in batches of 5.

Requirements:
- OpenAI API key in .env file as OPENAI_API_KEY
- MCP Supabase access (no env vars needed for DB)
"""

import os
import sys
import json
import re
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
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
        logging.FileHandler('blog_generation.log'),
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

# Import ranking utilities
sys.path.insert(0, os.path.dirname(__file__))
from ranking_utils import rank_professors

# Title patterns in French (varied)
TITLE_PATTERNS = [
    "Comment passer {course_title} avec succès?",
    "Guide complet pour réussir {course_title}",
    "Conseils et stratégies pour {course_title}",
    "Comment exceller dans {course_title}?",
    "Tout ce que vous devez savoir sur {course_title}",
    "Réussir {course_title}: Guide pratique",
    "Maîtriser {course_title}: Conseils d'experts",
    "Stratégies gagnantes pour {course_title}",
]

def get_difficulty_keywords(domain: str, title: str, description: str) -> Dict[str, int]:
    """
    Determine difficulty based on keywords and domain.
    Returns difficulty score (1-5) and reasoning.
    Math-oriented = more difficult.
    """
    text = f"{domain} {title} {description}".lower()
    
    # Math/quantitative keywords (higher difficulty)
    math_keywords = [
        'math', 'calcul', 'algèbre', 'géométrie', 'statistique', 'probabilité',
        'dérivée', 'intégrale', 'équation', 'formule', 'quantitatif', 'analyse',
        'finance', 'économétrie', 'modèle', 'optimisation'
    ]
    
    # Moderate difficulty keywords
    moderate_keywords = [
        'comptabilité', 'gestion', 'analyse', 'évaluation', 'stratégie'
    ]
    
    # Lower difficulty keywords
    lower_keywords = [
        'introduction', 'fondamentaux', 'bases', 'principes'
    ]
    
    math_count = sum(1 for kw in math_keywords if kw in text)
    moderate_count = sum(1 for kw in moderate_keywords if kw in text)
    lower_count = sum(1 for kw in lower_keywords if kw in text)
    
    # Calculate difficulty (1-5 scale)
    if math_count >= 3:
        difficulty = 5
    elif math_count >= 2:
        difficulty = 4
    elif math_count >= 1 or moderate_count >= 2:
        difficulty = 3
    elif lower_count >= 2:
        difficulty = 2
    else:
        difficulty = 3  # Default moderate
    
    return {
        'score': difficulty,
        'reasoning': f"Basé sur {math_count} mots-clés mathématiques/quantitatifs détectés"
    }

def get_study_strategy_by_domain(domain: str) -> str:
    """Get domain-specific study strategy guidance."""
    strategies = {
        'Mathématiques': """
- **Résolution de problèmes**: Pratiquez régulièrement des exercices et problèmes
- **Répétition espacée**: Révisiez les formules et concepts à intervalles réguliers
- **Approche pratique d'abord**: Commencez par résoudre des problèmes avant de lire la théorie
- **Mémorisation des formules**: Créez des fiches de formules essentielles
- **Analyse d'erreurs**: Examinez vos erreurs pour identifier les patterns
""",
        'Finance': """
- **Résolution de problèmes**: Pratiquez des calculs financiers régulièrement
- **Répétition espacée**: Mémorisez les formules de valorisation et d'analyse
- **Approche pratique d'abord**: Résolvez des cas pratiques avant la théorie
- **Rappel de formules**: Maîtrisez les formules clés (VAN, TRI, etc.)
- **Analyse d'erreurs**: Identifiez les erreurs courantes dans vos calculs
""",
        'Économie': """
- **Résolution de problèmes**: Pratiquez des exercices d'analyse économique
- **Répétition espacée**: Révisiez les modèles et théories économiques
- **Approche pratique d'abord**: Appliquez les concepts à des cas réels
- **Mémorisation des modèles**: Maîtrisez les graphiques et équations clés
- **Analyse d'erreurs**: Comprenez pourquoi certaines analyses échouent
""",
        'Comptabilité': """
- **Exercices de drill**: Pratiquez intensivement les écritures comptables
- **Analyse de patterns d'erreurs**: Identifiez vos erreurs récurrentes
- **Répétition espacée**: Révisiez les principes comptables régulièrement
- **Exercices pratiques**: Résolvez des problèmes de comptabilisation
- **Mémorisation des normes**: Apprenez les normes IFRS et NCECF
""",
        'Gestion des opérations': """
- **Frameworks**: Utilisez des cadres méthodologiques structurés
- **Cartes conceptuelles**: Visualisez les processus et flux
- **Flashcards**: Mémorisez les concepts clés et définitions
- **Études de cas**: Analysez des cas pratiques d'entreprises
- **Schémas visuels**: Représentez les systèmes opérationnels
""",
    }
    
    return strategies.get(domain, """
- **Répétition espacée**: Révisiez régulièrement les concepts clés
- **Pratique active**: Appliquez les concepts à des situations réelles
- **Organisation**: Structurez vos notes de manière logique
- **Révision régulière**: Ne laissez pas s'accumuler le matériel
""")

def get_professor_rankings_text(
    course_slug: str,
    ratings_data: List[Dict],
    metric: str
) -> Optional[str]:
    """Generate text about professor rankings (top 3 and bottom 3)."""
    if not ratings_data:
        return None
    
    results = rank_professors(ratings_data, metric=metric, top_n=3, aggregate=False)
    
    if not results['top'] and not results['bottom']:
        return None
    
    metric_labels = {
        'overall_rating': 'note globale',
        'difficulty_rating': 'niveau de difficulté'
    }
    
    label = metric_labels.get(metric, metric)
    text_parts = []
    
    if results['top']:
        top_profs = results['top'][:3]  # Top 3
        top_list = []
        for prof in top_profs:
            rating = prof.get(metric, 'N/A')
            if isinstance(rating, (int, float)):
                rating_str = f"{rating:.1f}/5.0"
            else:
                rating_str = str(rating)
            top_list.append(f"**{prof['professor_name']}** ({rating_str})")
        
        if len(top_list) == 1:
            text_parts.append(f"Meilleure {label}: {top_list[0]}")
        elif len(top_list) == 2:
            text_parts.append(f"Meilleures {label}s: {top_list[0]} et {top_list[1]}")
        else:
            text_parts.append(f"Meilleures {label}s: {', '.join(top_list[:-1])} et {top_list[-1]}")
    
    if results['bottom']:
        bottom_profs = results['bottom'][:3]  # Bottom 3
        bottom_list = []
        for prof in bottom_profs:
            rating = prof.get(metric, 'N/A')
            if isinstance(rating, (int, float)):
                rating_str = f"{rating:.1f}/5.0"
            else:
                rating_str = str(rating)
            bottom_list.append(f"**{prof['professor_name']}** ({rating_str})")
        
        if len(bottom_list) == 1:
            text_parts.append(f"{label.capitalize()} la plus faible: {bottom_list[0]}")
        elif len(bottom_list) == 2:
            text_parts.append(f"{label.capitalize()}s les plus faibles: {bottom_list[0]} et {bottom_list[1]}")
        else:
            text_parts.append(f"{label.capitalize()}s les plus faibles: {', '.join(bottom_list[:-1])} et {bottom_list[-1]}")
    
    return " ".join(text_parts) if text_parts else None

def generate_title(course_title: str) -> str:
    """Generate varied title based on course title."""
    import random
    pattern = random.choice(TITLE_PATTERNS)
    return pattern.format(course_title=course_title)

def count_words(text: str) -> int:
    """Count words in text (handles markdown)."""
    # Remove markdown syntax for word count
    text = re.sub(r'[#*`\[\]()]', '', text)
    text = re.sub(r'\n+', ' ', text)
    words = text.split()
    return len(words)

def calculate_similarity(content1: str, content2: str) -> float:
    """
    Simple similarity calculation using word overlap.
    Returns a score between 0 and 1 (higher = more similar).
    """
    # Simple word-based similarity
    words1 = set(re.findall(r'\b\w+\b', content1.lower()))
    words2 = set(re.findall(r'\b\w+\b', content2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0

def build_ai_prompt(
    course: Dict,
    website_description: str,
    professor_rankings_overall: Optional[str],
    professor_rankings_difficulty: Optional[str],
    difficulty_info: Dict[str, int],
    study_strategy: str
) -> str:
    """Build the AI prompt for content generation."""
    
    prompt = f"""Tu es un expert en rédaction de contenu éducatif en français. Génère un article de blog complet (minimum 700 mots, idéalement 900 mots) sur le cours suivant.

**Informations sur le cours:**
- Titre: {course['title_fr']}
- Code: {course['code']}
- Institution: {course.get('institution', 'ESG-UQAM')}
- Domaine: {course.get('domain', '')}
- Description: {website_description}

**Niveau de difficulté:** {difficulty_info['score']}/5 ({difficulty_info['reasoning']})

**Stratégies d'étude recommandées pour ce type de cours:**
{study_strategy}

**Classements des professeurs (RateMyProfessor):**
{f"- Note globale: {professor_rankings_overall}" if professor_rankings_overall else "- Aucune donnée disponible pour la note globale"}
{f"- Niveau de difficulté: {professor_rankings_difficulty}" if professor_rankings_difficulty else "- Aucune donnée disponible pour le niveau de difficulté"}

**Structure requise de l'article (en markdown):**

Utilise des titres h2 (##) pour les sections principales et h3 (###) pour les sous-sections. Ajoute une ligne vide entre chaque paragraphe et entre les sections pour une meilleure lisibilité.

## Aperçu du cours

(2-3 paragraphes avec une ligne vide entre chaque)
- Présentation générale du cours
- Son importance dans le programme
- Ce que les étudiants peuvent en attendre

## Niveau de difficulté

(1-2 paragraphes avec une ligne vide entre chaque)
- Score de difficulté: {difficulty_info['score']}/5
- Explication du niveau de difficulté
- Facteurs qui contribuent à cette difficulté

## Ce que vous apprendrez

(2-3 paragraphes avec une ligne vide entre chaque)
- Principaux sujets et concepts couverts
- Compétences développées
- Applications pratiques

## Meilleures stratégies d'étude pour ce cours

(3-4 paragraphes avec une ligne vide entre chaque)
- Stratégies spécifiques au domaine ({course.get('domain', '')})
- Techniques d'apprentissage recommandées
- Conseils pratiques pour la réussite

## Ce avec quoi les étudiants ont généralement des difficultés

(2-3 paragraphes avec une ligne vide entre chaque)
- Points communs de difficulté pour ce type de cours
- Erreurs fréquentes
- Comment les éviter

## Évaluations des professeurs

{f"- Note globale: {professor_rankings_overall}" if professor_rankings_overall else "- Aucune donnée de classement disponible pour la note globale"}
{f"- Niveau de difficulté: {professor_rankings_difficulty}" if professor_rankings_difficulty else "- Aucune donnée de classement disponible pour le niveau de difficulté"}

## Pourquoi le tutorat serait bénéfique pour ce cours

(2-3 paragraphes avec une ligne vide entre chaque)
- Avantages spécifiques du tutorat pour ce cours
- Comment un tuteur peut aider
- Bénéfices pour la réussite

## Résumé et prochaines étapes

(1-2 paragraphes avec une ligne vide entre chaque)
- Résumé des points clés
- Encouragement à utiliser les ressources disponibles
- Note: NE PAS ajouter de bouton d'action - il sera ajouté automatiquement après génération

**Instructions importantes:**
- Tout le contenu doit être en français
- Utilise le format markdown
- Le ton doit être professionnel mais accessible
- Minimum 700 mots, idéalement 900 mots
- Intègre naturellement les informations sur les professeurs si disponibles
- Sois spécifique au cours (ne sois pas générique)
- Utilise des exemples concrets quand c'est possible

Génère maintenant l'article complet en markdown."""

    return prompt

def generate_blog_content(
    course: Dict,
    website_description: str,
    professor_rankings_overall: Optional[str],
    professor_rankings_difficulty: Optional[str],
    difficulty_info: Dict[str, int],
    study_strategy: str
) -> Dict[str, any]:
    """Generate blog content using OpenAI API."""
    
    prompt = build_ai_prompt(
        course, website_description, professor_rankings_overall,
        professor_rankings_difficulty, difficulty_info, study_strategy
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",  # Using gpt-5-nano for best cost efficiency
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en rédaction de contenu éducatif en français. Tu génères des articles de blog complets, informatifs et engageants pour aider les étudiants à réussir leurs cours."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=2000,  # gpt-5-nano uses max_completion_tokens instead of max_tokens
            reasoning_effort="minimal",  # Prioritize content generation over reasoning
            verbosity="high"  # High verbosity for detailed, longer blog content
            # Note: gpt-5-nano doesn't support custom temperature, uses default (1)
        )
        
        content = response.choices[0].message.content
        
        # Generate title
        title = generate_title(course['title_fr'])
        
        # Generate meta description (first 150 chars of content, cleaned)
        meta_desc = re.sub(r'[#*`]', '', content)[:150].strip()
        if len(meta_desc) == 150:
            meta_desc += "..."
        
        # Extract H1 (first heading in content)
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        h1 = h1_match.group(1) if h1_match else title
        
        # Count words
        word_count = count_words(content)
        
        return {
            'content': content,
            'title': title,
            'h1': h1,
            'meta_description': meta_desc,
            'word_count': word_count,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error generating content for {course['code']}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_courses_with_descriptions() -> List[Dict]:
    """
    Fetch courses that have blog posts with website_description.
    Uses MCP Supabase access - this function will be called by assistant.
    """
    # This will be executed via MCP
    return []

def get_professor_ratings_for_course(course_slug: str) -> List[Dict]:
    """
    Fetch professor ratings for a course.
    Uses MCP Supabase access - this function will be called by assistant.
    """
    # This will be executed via MCP
    return []

def add_cta_button(content: str, course: Dict) -> str:
    """Add CTA button at the end of the content based on course active status."""
    is_active = course.get('active', False)
    course_slug = course.get('slug', '')
    course_code = course.get('code', '')
    
    # Remove any existing CTA button code that might have been generated by AI
    # Remove patterns like: <a href="...reservation..." class="cta-button">, <div class="cta-section">, etc.
    import re
    content = re.sub(r'<a[^>]*href="[^"]*reservation[^"]*"[^>]*class="cta-button"[^>]*>.*?</a>', '', content, flags=re.DOTALL)
    content = re.sub(r'<div[^>]*class="cta-section"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<a[^>]*href="/"[^>]*class="cta-button"[^>]*>.*?</a>', '', content, flags=re.DOTALL)
    
    # Clean up any extra blank lines
    content = content.rstrip() + '\n\n'
    
    button_html = ""
    if is_active:
        reservation_url = f"https://app.carredastutorat.com/cours/{course_slug}/reservation?code={course_code}&source=blog"
        button_html = f'<div class="cta-section">\n<a href="{reservation_url}" class="cta-button" target="_blank" rel="noopener noreferrer">Réserver une séance de tutorat</a>\n</div>'
    else:
        button_html = '<div class="cta-section">\n<a href="/" class="cta-button">Commencer le questionnaire</a>\n</div>'
    
    return content + button_html

def process_course(
    course: Dict,
    website_description: str,
    ratings_data: List[Dict]
) -> Dict[str, any]:
    """Process a single course and generate blog content."""
    
    logger.info(f"Processing course: {course['code']} - {course['title_fr']}")
    
    # Calculate difficulty
    difficulty_info = get_difficulty_keywords(
        course.get('domain', ''),
        course['title_fr'],
        website_description
    )
    
    # Get study strategy
    study_strategy = get_study_strategy_by_domain(course.get('domain', ''))
    
    # Get professor rankings
    professor_rankings_overall = None
    professor_rankings_difficulty = None
    
    if ratings_data:
        professor_rankings_overall = get_professor_rankings_text(
            course['slug'], ratings_data, 'overall_rating'
        )
        professor_rankings_difficulty = get_professor_rankings_text(
            course['slug'], ratings_data, 'difficulty_rating'
        )
    
    # Generate content
    result = generate_blog_content(
        course,
        website_description,
        professor_rankings_overall,
        professor_rankings_difficulty,
        difficulty_info,
        study_strategy
    )
    
    if not result['success']:
        return {
            'course_code': course['code'],
            'success': False,
            'error': result.get('error', 'Unknown error')
        }
    
    # Calculate similarity with existing posts (if any)
    # This will be done by comparing with other blog posts fetched via MCP
    similarity_score = None
    # Note: Similarity check will be performed by assistant using MCP to fetch existing posts
    
    # Add CTA button to content
    content_with_button = add_cta_button(result['content'], course)
    
    # Determine if indexable and publishable
    word_count = result['word_count']
    is_indexable = word_count >= 700  # Minimum 700 words
    should_publish = word_count >= 700  # Publish if meets minimum
    
    return {
        'course_slug': course['slug'],
        'course_code': course['code'],
        'title': result['title'],
        'h1': result['h1'],
        'content': content_with_button,
        'meta_description': result['meta_description'],
        'word_count': word_count,
        'similarity_score': similarity_score,
        'is_indexable': is_indexable,
        'published': should_publish,
        'success': True
    }

def main():
    """Main function - will be orchestrated by assistant with MCP access."""
    logger.info("Blog post generation script ready")
    logger.info("This script will be executed by the assistant with MCP Supabase access")
    logger.info("The assistant will:")
    logger.info("1. Fetch courses with descriptions")
    logger.info("2. Process in batches of 5")
    logger.info("3. Generate content using OpenAI")
    logger.info("4. Update blog posts in database")

if __name__ == '__main__':
    main()

