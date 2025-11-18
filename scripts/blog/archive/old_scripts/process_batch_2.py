#!/usr/bin/env python3
"""
Process second batch of 5 courses for blog post generation.
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

# Batch 2: Next 5 courses (all Finance, all active)
courses_batch = [
    {
        'course': {
            'slug': 'fin5521',
            'code': 'FIN5521',
            'title_fr': 'Analyse des valeurs mobilières I',
            'institution': 'ESG-UQAM',
            'domain': 'Finance',
            'active': True
        },
        'website_description': "Principes et modèles d'analyse. Analyse de la rentabilité. Bénéfice économique et comptable. Analyse de l'industrie. Techniques de prévision. Analyse du risque. La nature et la mesure du risque. Principes de gestion de portefeuilles. Risque et prime de risque. Analyse technique, efficience des marchés financiers.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'fin5523',
            'code': 'FIN5523',
            'title_fr': 'Marché obligataire et taux d\'intérêt',
            'institution': 'ESG-UQAM',
            'domain': 'Finance',
            'active': True
        },
        'website_description': "Taux d'intérêt et équilibre des marchés financiers, échéances et structure des taux d'intérêt. Durée du crédit et échéance: protection contre le risque de fluctuations des taux d'intérêts. Clauses de rachat. Analyse du risque d'insolvabilité. Impôts et autres influences gouvernementales sur l'allocation des ressources financières. Analyse des titres convertibles. Gestion de portefeuilles d'obligations; stratégies de gestion. Caractéristiques et évaluation des options.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'fin5550',
            'code': 'FIN5550',
            'title_fr': 'Options et contrats à terme',
            'institution': 'ESG-UQAM',
            'domain': 'Finance',
            'active': True
        },
        'website_description': "Ce cours a pour but d'analyser de façon rigoureuse le fonctionnement de ces nouveaux marchés financiers tant sur le plan théorique que pratique et de faire le lien entre ces marchés et ceux des titres traditionnels, surtout le marché obligataire. Plus spécifiquement, le cours vise à transmettre aux étudiants une compréhension solide de ces nouveaux instruments financiers, des principes d'évaluation qui leur sont applicables, des liens qui les unissent aux titres sous-jacents, et des stratégies de couverture, de spéculation, d'arbitrage et d'assurance de portefeuille qui les utilisent.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'fin5570',
            'code': 'FIN5570',
            'title_fr': 'Analyse et évaluation financière d\'entreprise',
            'institution': 'ESG-UQAM',
            'domain': 'Finance',
            'active': True
        },
        'website_description': "Ce cours vise à compléter les connaissances acquises dans le cadre du cours FIN3500 - Gestion financière afin de mieux préparer l'étudiant aux défis de l'évolution permanente de l'industrie des services et des produits financiers pour qu'il puisse assumer plus de responsabilités ou exercer de nouvelles fonctions selon les standards professionnels. Le cours développe des connaissances indispensables en analyse financière selon l'approche comptable et du marché afin de pouvoir analyser l'information financière et de placements recueillie dans un contexte économique donné pour établir les rendements et tendances futures et pouvoir émettre des opinions éclairées aux clients tant du côté achat que du côté vente. Le cours présente des techniques d'évaluation des entreprises tant traditionnelles que l'entreprise de la nouvelle économie. Les notions d'éthique et de déontologie en finance seront présentées et analysées. La gouvernance de la firme ainsi que les fusions et acquisitions seront étudiées.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'fin5580',
            'code': 'FIN5580',
            'title_fr': 'Finance multinationale',
            'institution': 'ESG-UQAM',
            'domain': 'Finance',
            'active': True
        },
        'website_description': "Permettre à l'étudiant d'avoir un aperçu général des domaines internationaux de la finance, lui fournir la base des concepts fondamentaux de la gestion financière multinationale, le rendre capable de comprendre les problèmes financiers qui confrontent les entreprises multinationales et pouvoir ébaucher une solution, et enfin pouvoir analyser la situation financière d'une compagnie multinationale et être capable de faire des études préliminaires à la prise de décision. - Les principaux marchés financiers. - Les institutions financières étrangères. - La réglementation et les contrôles élastiques. - La gestion financière: utilisation et acquisition rationnelles des fonds. - Les systèmes fiscaux et les mouvements des capitaux entre divers pays. - Interprétation des états financiers établis à l'étranger par les branches et filiales. - Le contrôle financier des filiales succursales, et représentation à l'étranger.",
        'ratings': []
    },
]

def main():
    print("=" * 60)
    print("BATCH 2: Generating Blog Posts for 5 Courses")
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
    output_file = os.path.join(os.path.dirname(__file__), 'batch_2_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("BATCH 2 COMPLETE")
    print("=" * 60)
    print(f"\nResults saved to: {output_file}")
    print(f"Successful: {sum(1 for r in results if r.get('success'))}/{len(results)}")
    print("\nNext step: Update database with generated content")

if __name__ == '__main__':
    main()
