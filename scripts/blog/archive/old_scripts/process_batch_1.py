#!/usr/bin/env python3
"""
Process first batch of 5 courses for blog post generation.
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

# Batch 1: First 5 courses
courses_batch = [
    {
        'course': {
            'slug': 'aot3220',
            'code': 'AOT3220',
            'title_fr': 'Recherche opérationnelle',
            'institution': 'ESG-UQAM',
            'domain': 'Gestion des opérations',
            'active': False
        },
        'website_description': "Ce cours a pour objectif de permettre à l'étudiant de se familiariser avec les techniques décisionnelles et d'optimisation de la recherche opérationnelle et plus spécifiquement de rendre l'étudiant apte à percevoir dans quel état se situe un problème donné, à identifier ses variables, à analyser et optimiser le phénomène à étudier et enfin d'être capable d'étudier et de comprendre les techniques connexes à celles présentées en séance. - Nature de la recherche opérationnelle - Cycle de décision - Modèle de décision - Décision en état d'ignorance - Programmation linéaire - Solution graphique - Solution algébrique - Méthode simplexe - Méthode de l'affectation - Affectation cyclique - Méthode du transport - Programmation dynamique - Décision en état de risque - Probabilités bayésiennes - Valeur de l'information - Théorie des files d'attente - Canal simple - Canaux multiples - Canal simple tronqué - Troncation absolue - Méthode de simulation Monte-Carlo - Réseau - Distribution Bêta - Variations des coûts et des temps - Décision en état de conflit - Théorie des jeux",
        'ratings': []
    },
    {
        'course': {
            'slug': 'aot4200',
            'code': 'AOT4200',
            'title_fr': 'Introduction à la gestion des opérations',
            'institution': 'ESG-UQAM',
            'domain': 'Gestion des opérations',
            'active': False
        },
        'website_description': "La gestion des opérations (GO) joue un rôle fondamental dans le fonctionnement des organisations. Elle permet de concevoir, de gérer et d'améliorer l'ensemble des processus des organisations (et de leurs réseaux) afin de créer de la valeur pour les clients. La GO est une discipline concrète qui permet aux organisations de s'adapter aux besoins changeants d'un contexte économique turbulent et d'atteindre leurs objectifs. L'objectif principal de ce cours est d'amener les étudiants à comprendre les principaux concepts et méthodes en GO. Les thèmes suivants seront couverts : La GO dans les organisations et ses interrelations avec les autres disciplines L'impact de la GO sur la compétitivité, la productivité et l'agilité des organisations Les rôles et les responsabilités en GO L'analyse d'un système opérationnel et de ses processus La planification de la demande et la gestion des ressources La planification des opérations et la gestion logistique L'utilisation des technologies en GO L'amélioration de la performance des processus",
        'ratings': []
    },
    {
        'course': {
            'slug': 'eco1300',
            'code': 'ECO1300',
            'title_fr': 'Analyse Microéconomique',
            'institution': 'ESG-UQAM',
            'domain': 'Économie',
            'active': False
        },
        'website_description': "Ce cours a pour objectif de permettre aux étudiants de prendre conscience de la complexité de l'environnement microéconomique dans lequel les individus, les ménages et les entreprises évoluent, de connaître les mécanismes par lesquels les variables économiques influencent leurs décisions et enfin, de les familiariser avec les aspects théoriques, institutionnels et politiques de l'analyse microéconomique appliquée à l'économie internationale. À la suite de ce cours, les étudiants devraient être en mesure de comprendre les principes de l'allocation des ressources dans les économies de marché et d'appliquer ces connaissances à la résolution de problèmes spécifiques à l'économie de l'entreprise, à l'économie industrielle et au commerce international.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'eco2400',
            'code': 'ECO2400',
            'title_fr': 'Analyse Macroéconomique',
            'institution': 'ESG-UQAM',
            'domain': 'Économie',
            'active': False
        },
        'website_description': "Ce cours a pour objectif de permettre aux étudiants de prendre conscience de la complexité de l'environnement macroéconomique dans lequel les individus, les ménages et les entreprises évoluent, de connaître les mécanismes par lesquels les variables économiques influencent leurs décisions et enfin, de les familiariser avec les aspects théoriques, institutionnels et politiques de l'analyse macroéconomique appliquée à l'économie internationale. À la suite de ce cours, les étudiants devraient être en mesure de comprendre les principales théories qui permettent d'expliquer l'évolution de la production, de l'emploi, des prix, des taux d'intérêt et des taux de change et d'en percevoir les implications relativement au rôle des autorités de la politique économique. Les grandes questions de la macroéconomie: chômage, inflation, croissance et cycles économiques. Faits stylisés de l'économie canadienne: consommation des ménages, investissements des entreprises, dépenses gouvernementales et flux internationaux de biens et services et de capitaux. La monnaie, le crédit et la détermination des taux d'intérêt. Les marchés financiers internationaux. La balance des paiements, les régimes de taux de change et le financement du commerce extérieur. Conduite de la politique monétaire au Canada. Déficits budgétaires des gouvernements et évolution de la dette publique. Le chômage, l'inflation et les politiques de stabilisation dans le contexte de l'économie mondiale. La croissance économique au Canada et dans le monde. Les prévisions économiques et l'analyse conjoncturelle.",
        'ratings': []
    },
    {
        'course': {
            'slug': 'eco8402',
            'code': 'ECO8402',
            'title_fr': "Environnement macroéconomique de l'entreprise",
            'institution': 'ESG-UQAM',
            'domain': 'Économie',
            'active': False
        },
        'website_description': "Ce cours a pour objectif de permettre aux participants d'acquérir une connaissance et une compréhension de l'environnement économique dans lequel évoluent les entreprises. Il identifie et analyse les éléments et les concepts sur lesquels s'appuie la prise de décisions. Bien que l'analyse porte avant tout sur les économies canadienne et québécoise, elle tient aussi compte de l'ouverture de ces dernières au commerce international ainsi que de l'intégration mondiale des marchés financiers. Les thèmes suivants sont traités : faits stylisés de l'économie canadienne: évolution de la consommation des ménages, des investissements des entreprises, des dépenses des gouvernements et des échanges internationaux de biens et services; la balance des paiements, le taux de change et le financement du commerce extérieur; les marchés financiers internationaux; la monnaie, le crédit et la détermination des taux d'intérêt; la conduite de la politique monétaire au Canada; la production, l'inflation et les politiques de stabilisation; les soldes budgétaires des gouvernements et la gestion de la dette publique; la croissance économique; les prévisions économiques et l'analyse conjoncturelle.",
        'ratings': []
    },
]

def main():
    print("=" * 60)
    print("BATCH 1: Generating Blog Posts for 5 Courses")
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
    output_file = os.path.join(os.path.dirname(__file__), 'batch_1_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("BATCH 1 COMPLETE")
    print("=" * 60)
    print(f"\nResults saved to: {output_file}")
    print(f"Successful: {sum(1 for r in results if r.get('success'))}/{len(results)}")
    print("\nNext step: Update database with generated content")

if __name__ == '__main__':
    main()

