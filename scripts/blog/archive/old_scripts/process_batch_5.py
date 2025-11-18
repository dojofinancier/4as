#!/usr/bin/env python3
"""
Process fifth batch of 3 courses for blog post generation.
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

# Batch 5: Final 3 courses (Accounting)
courses_batch = [
    {
        'course': {
            'slug': 'sco3240',
            'code': 'SCO3240',
            'title_fr': 'Comptabilité financière intermédiaire II',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': False
        },
        'website_description': "Ce cours traite des principaux contenus suivants : Comptabilisation, évaluation et présentation aux états financiers des diverses opérations relatives aux passifs financiers (courants et non courants) et aux capitaux propres; aux provisions; aux actifs et passifs éventuels; aux engagements contractuels; et aux événements postérieurs à la date de clôture, y compris les fondements conceptuels sur lesquels reposent ces normes et pratiques. Traitement comptable des modifications de conventions comptables, des révisions d'estimations et des corrections d'erreurs. Calcul des liquidités générées par les principales activités de financement, d'investissement et opérationnelles et préparation d'un état des flux de trésorerie.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'sco4008',
            'code': 'SCO4008',
            'title_fr': 'Impôt sur le revenu II',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': False
        },
        'website_description': "Ce cours traite des principaux contenus suivants : Calcul du revenu imposable et de l'impôt sur le revenu à payer par une société. Avantages à l'actionnaire. Dividendes réputés. Ventes d'actions/d'actifs. Déduction pour gain en capital. Roulement de biens en faveur d'une société. Remaniement du capital-actions d'une société. Imposition des revenus étrangers. Taxes à la consommation (TPS et TVQ).",
        'ratings': []
    },
    {
        'course': {
            'slug': 'sco4240',
            'code': 'SCO4240',
            'title_fr': 'Comptabilité financière avancée I',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': False
        },
        'website_description': "Ce cours traite des principaux contenus suivants : Placements dans des coentreprises, des filiales et des entreprises associées. Contrôle et influence notable. Utilisation et impact de la valeur d'acquisition et de la méthode de mise en équivalence. Achat d'actions, achat d'actifs et méthode de l'acquisition. États financiers consolidés et secteurs opérationnels. Détermination des justes valeurs et du goodwill. Informations relatives aux parties liées. États financiers intermédiaires.",
        'ratings': []
    },
]

def main():
    print("=" * 60)
    print("BATCH 5: Generating Blog Posts for 3 Courses")
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
        print(f"Processing {i}/3: {course['code']} - {course['title_fr']}")
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
    output_file = os.path.join(os.path.dirname(__file__), 'batch_5_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("BATCH 5 COMPLETE")
    print("=" * 60)
    print(f"\nResults saved to: {output_file}")
    print(f"Successful: {sum(1 for r in results if r.get('success'))}/{len(results)}")
    print("\nNext step: Update database with generated content")

if __name__ == '__main__':
    main()

