#!/usr/bin/env python3
"""
Process fourth batch of 5 courses for blog post generation.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the generation script functions
import importlib.util
script_path = os.path.join(os.path.dirname(__file__), 'generate-blog-posts.py')
spec = importlib.util.spec_from_file_location("generate_blog_posts", script_path)
generate_blog_posts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_blog_posts)
process_course = generate_blog_posts.process_course

# Batch 4: Next 5 courses (Accounting focus)
courses_batch = [
    {
        'course': {
            'slug': 'sco2000',
            'code': 'SCO2000',
            'title_fr': 'Contrôle de gestion',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': True
        },
        'website_description': "La connaissance et l'aptitude à utiliser les principes de la comptabilité nécessaires à l'administration d'une industrie. Notions élémentaires de comptabilité industrielle. Planification et contrôle budgétaire dans l'entreprise industrielle. Le prix de revient normal et standard. Le comportement des coûts: interaction coûts-volume-bénéfice. Les coûts proportionnels. Les coûts pertinents et la prise de décision à court terme: utilisation des ressources existantes. La rentabilité des investissements et la prise de décision à long terme. L'étudiant pourra suivre, sur une base facultative, des laboratoires consacrés à l'application des concepts présentés dans les cours.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'sco2001',
            'code': 'SCO2001',
            'title_fr': 'Comptabilité de management II',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': True
        },
        'website_description': "Ce cours traite des principaux contenus suivants : Fonctions de la comptabilité de management. Les modes de fabrication sur commande et uniforme. Les marges et la prise de décision. L'analyse coûts-volumes-bénéfices et les éléments pertinents à la prise de décision. Études de cas.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'sco2240',
            'code': 'SCO2240',
            'title_fr': 'Comptabilité financière intermédiaire I',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': True
        },
        'website_description': "Ce cours traite des principaux contenus suivants : Stocks. Créances. Placements comme actifs financiers. État du résultat net et du résultat global. Activités abandonnées. Immobilisations corporelles. Actifs incorporels. Échanges d'actifs. Aide et subvention publiques. Constatation des produits.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'sco3001',
            'code': 'SCO3001',
            'title_fr': 'Comptabilité de management II',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': True
        },
        'website_description': "Ce cours traite des principaux contenus suivants : Approfondissement des notions de gestion de coûts et de planification. D'une part, la comptabilité par activité, la production conjointe, les processus et les sections auxiliaires et, d'autre part, gérer le flux de trésorerie courant en développant des prévisions financières et des budgets, en enregistrant des informations sur les performances et en utilisant des outils de prise de décision à court terme. Outils de planification à court terme: Budgets des opérations. Budgets financiers. Gestion du processus de budgétisation (participation). Comptabilité de caisse. Éléments financiers pertinents. Budget flexible. Analyse d'écarts. Contrôles des dépenses discrétionnaires (budget base zéro, budget par activité, budgets spéciaux, financement des projets). Études de cas.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'sco3008',
            'code': 'SCO3008',
            'title_fr': 'Impôt sur le revenu I',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': False
        },
        'website_description': "Ce cours traite des principaux contenus suivants : Calcul du revenu d'emploi, d'entreprise et de biens. Amortissement des biens corporels et incorporels. Calcul du gain en capital. Autres revenus et autres déductions. Calcul du revenu imposable des particuliers et plus particulièrement des pertes à reporter. Calcul de l'impôt à payer des particuliers.",
        'ratings': []
    },
]

def main():
    print("=" * 60)
    print("BATCH 4: Generating Blog Posts for 5 Courses")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    
    results = []
    
    for i, course_info in enumerate(courses_batch, 1):
        course = course_info['course']
        website_description = course_info['website_description']
        ratings = course_info['ratings']
        
        print(f"\n{'='*60}")
        print(f"Processing {i}/5: {course['code']} - {course['title_fr']}")
        print(f"{'='*60}\n")
        
        try:
            result = process_course(
                course=course,
                website_description=website_description,
                ratings_data=ratings
            )
            
            if result['success']:
                print(f"[OK] Generated: {result['word_count']} words")
                print(f"[OK] Title: {result['title']}")
                results.append(result)
            else:
                print(f"[ERROR] Failed: {result.get('error', 'Unknown error')}")
                results.append({
                    'success': False,
                    'course_code': course['code'],
                    'error': result.get('error', 'Unknown error')
                })
                
        except Exception as e:
            print(f"[ERROR] Exception: {str(e)}")
            results.append({
                'success': False,
                'course_code': course['code'],
                'error': str(e)
            })
    
    # Save results
    output_file = os.path.join(os.path.dirname(__file__), 'batch_4_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("BATCH 4 COMPLETE")
    print("=" * 60)
    print(f"\nResults saved to: {output_file}")
    print(f"Successful: {sum(1 for r in results if r.get('success'))}/{len(results)}")
    print("\nNext step: Update database with generated content")

if __name__ == '__main__':
    main()

