#!/usr/bin/env python3
"""
Process third batch of 5 courses for blog post generation.
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

# Batch 3: Next 5 courses (mix of domains)
courses_batch = [
    {
        'course': {
            'slug': 'fin8415',
            'code': 'FIN8415',
            'title_fr': 'Gestion financière',
            'institution': 'ESG-UQAM',
            'domain': 'Finance',
            'active': True
        },
        'website_description': "Ce cours vise l'initiation de l'étudiant aux techniques permettant l'analyse et la prévision des fonds dont l'entreprise a besoin. On y aborde également les choix requis à court et à long terme pour l'allocation optimale des ressources d'une entreprise à ses différents secteurs d'activités. On y aborde aussi les notions d'allocation optimale de ressources primaires entre différentes possibilités d'investissement. On y traite des différentes sources de financement disponibles et des choix nécessaires en termes de coûts et de risques pour l'atteinte d'une politique financière optimale.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'mat0343',
            'code': 'MAT0343',
            'title_fr': 'Calcul différentiel',
            'institution': 'ESG-UQAM',
            'domain': 'Mathématiques',
            'active': True
        },
        'website_description': "Introduction au calcul différentiel et intégral (du point de vue des applications). Concept de fonction. Rappels concernant les exposants. Fonctions exponentielles, logarithmiques et puissances. Fonctions trigonométriques. Suites numériques. Limites et continuité de fonctions. Dérivée d'une fonction. Dérivées d'ordre supérieur. Applications de la dérivée.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'mat1002',
            'code': 'MAT1002',
            'title_fr': 'Introduction aux méthodes quantitatives appliquées à la gestion',
            'institution': 'ESG-UQAM',
            'domain': 'Mathématiques',
            'active': True
        },
        'website_description': "Ce cours est offert hors programme (CRÉDITS NON COMPTABILISÉS). Cycle : 1 Type de cours : Magistral Nombre de crédits : 3 Discipline : Mathématiques Développer chez l'étudiant des connaissances, des habiletés et des outils de travail (de base) de type mathématique, statistique et informatique considérés comme nécessaires pour suivre avec intérêt et efficacité son programme d'études: également démystifier l'ordinateur et développer le goût des méthodes quantitatives. Introduction au chiffrier électronique. Utilisation de ce chiffrier pour le rappel du langage mathématique de base: expressions algébriques, expressions fonctionnelles, expressions ensemblestes et langage graphique, résolutions d'équations. Étude de la droite. Résolution graphique de systèmes d'équations et d'inéquations. Intérêts simple et composé. Analyse et interprétation de données mathématiques et statistiques de gestion.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'sco1240',
            'code': 'SCO1240',
            'title_fr': 'Introduction à la comptabilité financière',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': True
        },
        'website_description': "Ce cours traite des principaux contenus suivants : notions de débit et de crédit; nature des comptes; équation comptable fondamentale; cycle comptable; constatation des produits et des charges, rapprochement des charges et des produits, charges payées d'avance et à payer, produits constatés d'avance et à recevoir; immobilisations, amortissements, gains et pertes sur cession d'immobilisations; évaluation des stocks et coûts des marchandises vendues; comptabilité d'engagement et comptabilité de trésorerie; encaisse et placements temporaires; gestion et contrôle interne de la trésorerie; journaux et grands livres auxiliaires; traitement de la paie; établissement de la balance de vérification; régularisations de fin de période; préparation de l'état de la situation financière, de l'état des résultats et de l'état des variations des capitaux propres.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'sco1250',
            'code': 'SCO1250',
            'title_fr': 'Introductions aux sciences comptables',
            'institution': 'ESG-UQAM',
            'domain': 'Comptabilité',
            'active': True
        },
        'website_description': "Le cours a pour objet de présenter le rôle de l'information financière dans la prise de décisions économiques. Au terme de ce cours, l'étudiant sera capable de comprendre la nature de l'information financière préparée selon les Normes internationales d'information financière (IFRS) et les Normes comptables pour les entreprises à capital fermé (NCECF), de différencier les besoins des utilisateurs des rapports financiers, de sélectionner l'information pertinente selon le type de décisions économiques, d'évaluer les limites de l'information financière, de comprendre la terminologie utilisée, d'utiliser la littérature pour mieux saisir les problématiques financières et d'être conscient de l'importance de l'éthique dans l'exercice de la profession. Ce cours traite des principaux contenus suivants : - utilisateurs de l'information financière. Rôle et intervention des experts-comptables; - concepts fondamentaux des différents domaines liés aux sciences comptables; - nature et utilité de l'information financière; - analyse des opérations sur la base de l'équation comptable; - information financière portant sur les résultats, les flux de trésorerie, les ressources économiques et les sources de capitaux.",
        'ratings': []
    },
]

def main():
    print("=" * 60)
    print("BATCH 3: Generating Blog Posts for 5 Courses")
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
    output_file = os.path.join(os.path.dirname(__file__), 'batch_3_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("BATCH 3 COMPLETE")
    print("=" * 60)
    print(f"\nResults saved to: {output_file}")
    print(f"Successful: {sum(1 for r in results if r.get('success'))}/{len(results)}")
    print("\nNext step: Update database with generated content")

if __name__ == '__main__':
    main()

