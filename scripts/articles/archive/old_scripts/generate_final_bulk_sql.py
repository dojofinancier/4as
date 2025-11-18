#!/usr/bin/env python3
"""
Final script to match articles with outlines and generate bulk UPDATE SQL.
Uses the efficient UPDATE ... FROM VALUES pattern.
"""

import json
import sys

# Articles from database query (217 articles)
articles = [
    {"slug": "approche-pratique-de-la-methodologie-universitaire", "title": "Approche pratique de la méthodologie universitaire"},
    {"slug": "approche-pratique-de-la-microeconomie", "title": "Approche pratique de la microéconomie"},
    {"slug": "approche-pratique-de-la-motivation", "title": "Approche pratique de la motivation"},
    {"slug": "approche-pratique-de-la-planification-de-session", "title": "Approche pratique de la planification de session"},
    {"slug": "approche-pratique-de-le-management", "title": "Approche pratique de le management"},
    {"slug": "approche-pratique-de-les-etudes-de-cas", "title": "Approche pratique de les études de cas"},
    {"slug": "approche-pratique-de-les-examens-difficiles", "title": "Approche pratique de les examens difficiles"},
    {"slug": "approche-pratique-de-les-revisions", "title": "Approche pratique de les révisions"},
    {"slug": "approche-pratique-de-les-statistiques", "title": "Approche pratique de les statistiques"},
    {"slug": "approche-pratique-de-letude-des-matieres-difficiles", "title": "Approche pratique de l'étude des matières difficiles"},
    {"slug": "approche-pratique-de-notion", "title": "Approche pratique de Notion"},
    {"slug": "bases-essentielles-de-excel", "title": "Bases essentielles de Excel"},
    {"slug": "bases-essentielles-de-la-comptabilite", "title": "Bases essentielles de la comptabilité"},
    {"slug": "bases-essentielles-de-la-concentration", "title": "Bases essentielles de la concentration"},
    {"slug": "bases-essentielles-de-la-finance-de-base", "title": "Bases essentielles de la finance de base"},
    {"slug": "bases-essentielles-de-la-gestion-du-temps", "title": "Bases essentielles de la gestion du temps"},
    {"slug": "bases-essentielles-de-la-lecture-academique", "title": "Bases essentielles de la lecture académique"},
    {"slug": "bases-essentielles-de-la-memorisation-active", "title": "Bases essentielles de la mémorisation active"},
    {"slug": "bases-essentielles-de-la-microeconomie", "title": "Bases essentielles de la microéconomie"},
    {"slug": "bases-essentielles-de-la-prise-de-notes", "title": "Bases essentielles de la prise de notes"},
    {"slug": "bases-essentielles-de-la-reduction-du-stress", "title": "Bases essentielles de la réduction du stress"},
    {"slug": "bases-essentielles-de-le-marketing", "title": "Bases essentielles de le marketing"},
    {"slug": "bases-essentielles-de-le-sommeil-etudiant", "title": "Bases essentielles de le sommeil étudiant"},
    {"slug": "bases-essentielles-de-les-presentations-orales", "title": "Bases essentielles de les présentations orales"},
    {"slug": "bases-essentielles-de-les-projets-de-groupe", "title": "Bases essentielles de les projets de groupe"},
    {"slug": "bases-essentielles-de-les-revisions", "title": "Bases essentielles de les révisions"},
    {"slug": "bases-essentielles-de-les-statistiques", "title": "Bases essentielles de les statistiques"},
    {"slug": "bases-essentielles-de-lorganisation-personnelle", "title": "Bases essentielles de l'organisation personnelle"},
    {"slug": "comment-developper-ses-competences-en-la-comprehension-des-textes-complexes", "title": "Comment développer ses compétences en la compréhension des textes complexes"},
    {"slug": "comment-developper-ses-competences-en-la-concentration", "title": "Comment développer ses compétences en la concentration"},
    {"slug": "comment-developper-ses-competences-en-la-finance-de-base", "title": "Comment développer ses compétences en la finance de base"},
    {"slug": "comment-developper-ses-competences-en-la-gestion-du-temps", "title": "Comment développer ses compétences en la gestion du temps"},
    {"slug": "comment-developper-ses-competences-en-la-memorisation-active", "title": "Comment développer ses compétences en la mémorisation active"},
    {"slug": "comment-developper-ses-competences-en-la-methodologie-universitaire", "title": "Comment développer ses compétences en la méthodologie universitaire"},
    {"slug": "comment-developper-ses-competences-en-la-microeconomie", "title": "Comment développer ses compétences en la microéconomie"},
    {"slug": "comment-developper-ses-competences-en-la-resolution-de-problemes", "title": "Comment développer ses compétences en la résolution de problèmes"},
    {"slug": "comment-developper-ses-competences-en-le-management", "title": "Comment développer ses compétences en le management"},
    {"slug": "comment-developper-ses-competences-en-les-examens-difficiles", "title": "Comment développer ses compétences en les examens difficiles"},
    {"slug": "comment-developper-ses-competences-en-letude-des-matieres-difficiles", "title": "Comment développer ses compétences en l'étude des matières difficiles"},
    {"slug": "comment-developper-ses-competences-en-notion", "title": "Comment développer ses compétences en Notion"},
    {"slug": "comment-maitriser-excel", "title": "Comment maîtriser Excel"},
    {"slug": "comment-maitriser-la-concentration", "title": "Comment maîtriser la concentration"},
    {"slug": "comment-maitriser-la-finance-de-base", "title": "Comment maîtriser la finance de base"},
    {"slug": "comment-maitriser-la-gestion-du-temps", "title": "Comment maîtriser la gestion du temps"},
    {"slug": "comment-maitriser-la-lecture-academique", "title": "Comment maîtriser la lecture académique"},
    {"slug": "comment-maitriser-la-microeconomie", "title": "Comment maîtriser la microéconomie"},
    {"slug": "comment-maitriser-la-motivation", "title": "Comment maîtriser la motivation"},
    {"slug": "comment-maitriser-la-prise-de-notes", "title": "Comment maîtriser la prise de notes"},
    {"slug": "comment-maitriser-la-reduction-du-stress", "title": "Comment maîtriser la réduction du stress"},
    {"slug": "comment-maitriser-lanalyse-financiere", "title": "Comment maîtriser l'analyse financière"},
    {"slug": "comment-maitriser-les-etudes-de-cas", "title": "Comment maîtriser les études de cas"},
    {"slug": "comment-maitriser-les-examens-difficiles", "title": "Comment maîtriser les examens difficiles"},
    {"slug": "comment-maitriser-les-projets-de-groupe", "title": "Comment maîtriser les projets de groupe"},
    {"slug": "comment-maitriser-les-strategies-dexamen", "title": "Comment maîtriser les stratégies d'examen"},
    {"slug": "comment-maitriser-notion", "title": "Comment maîtriser Notion"},
    {"slug": "comment-saméliorer-en-excel", "title": "Comment s'améliorer en Excel"},
    {"slug": "comment-saméliorer-en-la-comptabilite", "title": "Comment s'améliorer en la comptabilité"},
    {"slug": "comment-saméliorer-en-la-concentration", "title": "Comment s'améliorer en la concentration"},
    {"slug": "comment-saméliorer-en-la-gestion-du-temps", "title": "Comment s'améliorer en la gestion du temps"},
    {"slug": "comment-saméliorer-en-la-memorisation-active", "title": "Comment s'améliorer en la mémorisation active"},
    {"slug": "comment-saméliorer-en-la-methodologie-universitaire", "title": "Comment s'améliorer en la méthodologie universitaire"},
    {"slug": "comment-saméliorer-en-la-motivation", "title": "Comment s'améliorer en la motivation"},
    {"slug": "comment-saméliorer-en-la-planification-de-session", "title": "Comment s'améliorer en la planification de session"},
    {"slug": "comment-saméliorer-en-la-prise-de-notes", "title": "Comment s'améliorer en la prise de notes"},
    {"slug": "comment-saméliorer-en-la-reduction-du-stress", "title": "Comment s'améliorer en la réduction du stress"},
    {"slug": "comment-saméliorer-en-le-raisonnement-logique", "title": "Comment s'améliorer en le raisonnement logique"},
    {"slug": "comment-saméliorer-en-les-etudes-de-cas", "title": "Comment s'améliorer en les études de cas"},
    {"slug": "comment-saméliorer-en-les-examens-difficiles", "title": "Comment s'améliorer en les examens difficiles"},
    {"slug": "comment-saméliorer-en-les-presentations-orales", "title": "Comment s'améliorer en les présentations orales"},
    {"slug": "comment-saméliorer-en-les-revisions", "title": "Comment s'améliorer en les révisions"},
    {"slug": "comprendre-facilement-la-comprehension-des-textes-complexes", "title": "Comprendre facilement la compréhension des textes complexes"},
    {"slug": "comprendre-facilement-la-comptabilite", "title": "Comprendre facilement la comptabilité"},
    {"slug": "comprendre-facilement-la-concentration", "title": "Comprendre facilement la concentration"},
    {"slug": "comprendre-facilement-la-finance-de-base", "title": "Comprendre facilement la finance de base"},
    {"slug": "comprendre-facilement-la-lecture-academique", "title": "Comprendre facilement la lecture académique"},
    {"slug": "comprendre-facilement-la-memorisation-active", "title": "Comprendre facilement la mémorisation active"},
    {"slug": "comprendre-facilement-la-methodologie-universitaire", "title": "Comprendre facilement la méthodologie universitaire"},
    {"slug": "comprendre-facilement-la-microeconomie", "title": "Comprendre facilement la microéconomie"},
    {"slug": "comprendre-facilement-la-motivation", "title": "Comprendre facilement la motivation"},
    {"slug": "comprendre-facilement-la-reduction-du-stress", "title": "Comprendre facilement la réduction du stress"},
    {"slug": "comprendre-facilement-la-resolution-de-problemes", "title": "Comprendre facilement la résolution de problèmes"},
    {"slug": "comprendre-facilement-le-management", "title": "Comprendre facilement le management"},
    {"slug": "comprendre-facilement-le-marketing", "title": "Comprendre facilement le marketing"},
    {"slug": "comprendre-facilement-les-etudes-de-cas", "title": "Comprendre facilement les études de cas"},
    {"slug": "comprendre-facilement-les-projets-de-groupe", "title": "Comprendre facilement les projets de groupe"},
    {"slug": "comprendre-facilement-les-revisions", "title": "Comprendre facilement les révisions"},
    {"slug": "comprendre-facilement-letude-des-matieres-difficiles", "title": "Comprendre facilement l'étude des matières difficiles"},
    {"slug": "erreurs-courantes-a-eviter-en-excel", "title": "Erreurs courantes à éviter en Excel"},
    {"slug": "erreurs-courantes-a-eviter-en-la-comprehension-des-textes-complexes", "title": "Erreurs courantes à éviter en la compréhension des textes complexes"},
    {"slug": "erreurs-courantes-a-eviter-en-la-comptabilite", "title": "Erreurs courantes à éviter en la comptabilité"},
    {"slug": "erreurs-courantes-a-eviter-en-la-gestion-du-temps", "title": "Erreurs courantes à éviter en la gestion du temps"},
    {"slug": "erreurs-courantes-a-eviter-en-la-memorisation-active", "title": "Erreurs courantes à éviter en la mémorisation active"},
    {"slug": "erreurs-courantes-a-eviter-en-la-motivation", "title": "Erreurs courantes à éviter en la motivation"},
    {"slug": "erreurs-courantes-a-eviter-en-la-planification-de-session", "title": "Erreurs courantes à éviter en la planification de session"},
    {"slug": "erreurs-courantes-a-eviter-en-le-marketing", "title": "Erreurs courantes à éviter en le marketing"},
    {"slug": "erreurs-courantes-a-eviter-en-le-raisonnement-logique", "title": "Erreurs courantes à éviter en le raisonnement logique"},
    {"slug": "erreurs-courantes-a-eviter-en-les-etudes-de-cas", "title": "Erreurs courantes à éviter en les études de cas"},
    {"slug": "erreurs-courantes-a-eviter-en-les-presentations-orales", "title": "Erreurs courantes à éviter en les présentations orales"},
    {"slug": "erreurs-courantes-a-eviter-en-les-projets-de-groupe", "title": "Erreurs courantes à éviter en les projets de groupe"},
    {"slug": "erreurs-courantes-a-eviter-en-les-statistiques", "title": "Erreurs courantes à éviter en les statistiques"},
    {"slug": "erreurs-courantes-a-eviter-en-les-strategies-dexamen", "title": "Erreurs courantes à éviter en les stratégies d'examen"},
    {"slug": "erreurs-courantes-a-eviter-en-letude-des-matieres-difficiles", "title": "Erreurs courantes à éviter en l'étude des matières difficiles"},
    {"slug": "erreurs-courantes-a-eviter-en-notion", "title": "Erreurs courantes à éviter en Notion"},
    {"slug": "guide-complet-pour-comprendre-la-comprehension-des-textes-complexes", "title": "Guide complet pour comprendre la compréhension des textes complexes"},
    {"slug": "guide-complet-pour-comprendre-la-comptabilite", "title": "Guide complet pour comprendre la comptabilité"},
    {"slug": "guide-complet-pour-comprendre-la-finance-de-base", "title": "Guide complet pour comprendre la finance de base"},
    {"slug": "guide-complet-pour-comprendre-la-gestion-du-temps", "title": "Guide complet pour comprendre la gestion du temps"},
    {"slug": "guide-complet-pour-comprendre-la-memorisation-active", "title": "Guide complet pour comprendre la mémorisation active"},
    {"slug": "guide-complet-pour-comprendre-la-planification-de-session", "title": "Guide complet pour comprendre la planification de session"},
    {"slug": "guide-complet-pour-comprendre-les-etudes-de-cas", "title": "Guide complet pour comprendre les études de cas"},
    {"slug": "guide-complet-pour-comprendre-les-presentations-orales", "title": "Guide complet pour comprendre les présentations orales"},
    {"slug": "guide-complet-pour-comprendre-les-revisions", "title": "Guide complet pour comprendre les révisions"},
    {"slug": "guide-complet-pour-comprendre-les-strategies-dexamen", "title": "Guide complet pour comprendre les stratégies d'examen"},
    {"slug": "guide-complet-pour-comprendre-letude-des-matieres-difficiles", "title": "Guide complet pour comprendre l'étude des matières difficiles"},
    {"slug": "guide-complet-pour-comprendre-lorganisation-personnelle", "title": "Guide complet pour comprendre l'organisation personnelle"},
    {"slug": "introduction-pratique-a-la-comptabilite", "title": "Introduction pratique à la comptabilité"},
    {"slug": "introduction-pratique-a-la-memorisation-active", "title": "Introduction pratique à la mémorisation active"},
    {"slug": "introduction-pratique-a-la-methodologie-universitaire", "title": "Introduction pratique à la méthodologie universitaire"},
    {"slug": "introduction-pratique-a-la-microeconomie", "title": "Introduction pratique à la microéconomie"},
    {"slug": "introduction-pratique-a-la-motivation", "title": "Introduction pratique à la motivation"},
    {"slug": "introduction-pratique-a-la-reduction-du-stress", "title": "Introduction pratique à la réduction du stress"},
    {"slug": "introduction-pratique-a-le-marketing", "title": "Introduction pratique à le marketing"},
    {"slug": "introduction-pratique-a-les-etudes-de-cas", "title": "Introduction pratique à les études de cas"},
    {"slug": "introduction-pratique-a-les-presentations-orales", "title": "Introduction pratique à les présentations orales"},
    {"slug": "introduction-pratique-a-letude-des-matieres-difficiles", "title": "Introduction pratique à l'étude des matières difficiles"},
    {"slug": "methode-rapide-pour-la-comptabilite", "title": "Méthode rapide pour la comptabilité"},
    {"slug": "methode-rapide-pour-la-concentration", "title": "Méthode rapide pour la concentration"},
    {"slug": "methode-rapide-pour-la-finance-de-base", "title": "Méthode rapide pour la finance de base"},
    {"slug": "methode-rapide-pour-la-gestion-du-temps", "title": "Méthode rapide pour la gestion du temps"},
    {"slug": "methode-rapide-pour-la-lecture-academique", "title": "Méthode rapide pour la lecture académique"},
    {"slug": "methode-rapide-pour-la-methodologie-universitaire", "title": "Méthode rapide pour la méthodologie universitaire"},
    {"slug": "methode-rapide-pour-la-microeconomie", "title": "Méthode rapide pour la microéconomie"},
    {"slug": "methode-rapide-pour-la-prise-de-notes", "title": "Méthode rapide pour la prise de notes"},
    {"slug": "methode-rapide-pour-la-reduction-du-stress", "title": "Méthode rapide pour la réduction du stress"},
    {"slug": "methode-rapide-pour-le-management", "title": "Méthode rapide pour le management"},
    {"slug": "methode-rapide-pour-le-marketing", "title": "Méthode rapide pour le marketing"},
    {"slug": "methode-rapide-pour-le-raisonnement-logique", "title": "Méthode rapide pour le raisonnement logique"},
    {"slug": "methode-rapide-pour-les-strategies-dexamen", "title": "Méthode rapide pour les stratégies d'examen"},
    {"slug": "methode-rapide-pour-letude-des-matieres-difficiles", "title": "Méthode rapide pour l'étude des matières difficiles"},
    {"slug": "methode-simple-pour-apprendre-la-concentration", "title": "Méthode simple pour apprendre la concentration"},
    {"slug": "methode-simple-pour-apprendre-la-microeconomie", "title": "Méthode simple pour apprendre la microéconomie"},
    {"slug": "methode-simple-pour-apprendre-la-motivation", "title": "Méthode simple pour apprendre la motivation"},
    {"slug": "methode-simple-pour-apprendre-la-prise-de-notes", "title": "Méthode simple pour apprendre la prise de notes"},
    {"slug": "methode-simple-pour-apprendre-lanalyse-financiere", "title": "Méthode simple pour apprendre l'analyse financière"},
    {"slug": "methode-simple-pour-apprendre-le-management", "title": "Méthode simple pour apprendre le management"},
    {"slug": "methode-simple-pour-apprendre-les-revisions", "title": "Méthode simple pour apprendre les révisions"},
    {"slug": "methode-simple-pour-apprendre-les-statistiques", "title": "Méthode simple pour apprendre les statistiques"},
    {"slug": "methode-simple-pour-apprendre-les-strategies-dexamen", "title": "Méthode simple pour apprendre les stratégies d'examen"},
    {"slug": "methode-simple-pour-apprendre-letude-des-matieres-difficiles", "title": "Méthode simple pour apprendre l'étude des matières difficiles"},
    {"slug": "optimiser-sa-reussite-en-la-comprehension-des-textes-complexes", "title": "Optimiser sa réussite en la compréhension des textes complexes"},
    {"slug": "optimiser-sa-reussite-en-la-comptabilite", "title": "Optimiser sa réussite en la comptabilité"},
    {"slug": "optimiser-sa-reussite-en-la-concentration", "title": "Optimiser sa réussite en la concentration"},
    {"slug": "optimiser-sa-reussite-en-la-memorisation-active", "title": "Optimiser sa réussite en la mémorisation active"},
    {"slug": "optimiser-sa-reussite-en-la-microeconomie", "title": "Optimiser sa réussite en la microéconomie"},
    {"slug": "optimiser-sa-reussite-en-la-planification-de-session", "title": "Optimiser sa réussite en la planification de session"},
    {"slug": "optimiser-sa-reussite-en-la-resolution-de-problemes", "title": "Optimiser sa réussite en la résolution de problèmes"},
    {"slug": "optimiser-sa-reussite-en-le-management", "title": "Optimiser sa réussite en le management"},
    {"slug": "optimiser-sa-reussite-en-le-marketing", "title": "Optimiser sa réussite en le marketing"},
    {"slug": "optimiser-sa-reussite-en-le-raisonnement-logique", "title": "Optimiser sa réussite en le raisonnement logique"},
    {"slug": "optimiser-sa-reussite-en-le-sommeil-etudiant", "title": "Optimiser sa réussite en le sommeil étudiant"},
    {"slug": "optimiser-sa-reussite-en-les-etudes-de-cas", "title": "Optimiser sa réussite en les études de cas"},
    {"slug": "optimiser-sa-reussite-en-les-strategies-dexamen", "title": "Optimiser sa réussite en les stratégies d'examen"},
    {"slug": "optimiser-sa-reussite-en-lorganisation-personnelle", "title": "Optimiser sa réussite en l'organisation personnelle"},
    {"slug": "secrets-pour-reussir-en-excel", "title": "Secrets pour réussir en Excel"},
    {"slug": "secrets-pour-reussir-en-la-memorisation-active", "title": "Secrets pour réussir en la mémorisation active"},
    {"slug": "secrets-pour-reussir-en-la-methodologie-universitaire", "title": "Secrets pour réussir en la méthodologie universitaire"},
    {"slug": "secrets-pour-reussir-en-lanalyse-financiere", "title": "Secrets pour réussir en l'analyse financière"},
    {"slug": "secrets-pour-reussir-en-le-marketing", "title": "Secrets pour réussir en le marketing"},
    {"slug": "secrets-pour-reussir-en-le-sommeil-etudiant", "title": "Secrets pour réussir en le sommeil étudiant"},
    {"slug": "secrets-pour-reussir-en-les-projets-de-groupe", "title": "Secrets pour réussir en les projets de groupe"},
    {"slug": "secrets-pour-reussir-en-les-revisions", "title": "Secrets pour réussir en les révisions"},
    {"slug": "secrets-pour-reussir-en-letude-des-matieres-difficiles", "title": "Secrets pour réussir en l'étude des matières difficiles"},
    {"slug": "secrets-pour-reussir-en-lorganisation-personnelle", "title": "Secrets pour réussir en l'organisation personnelle"},
    {"slug": "strategies-efficaces-pour-progresser-la-comprehension-des-textes-complexes", "title": "Stratégies efficaces pour progresser la compréhension des textes complexes"},
    {"slug": "strategies-efficaces-pour-progresser-la-comptabilite", "title": "Stratégies efficaces pour progresser la comptabilité"},
    {"slug": "strategies-efficaces-pour-progresser-la-concentration", "title": "Stratégies efficaces pour progresser la concentration"},
    {"slug": "strategies-efficaces-pour-progresser-la-lecture-academique", "title": "Stratégies efficaces pour progresser la lecture académique"},
    {"slug": "strategies-efficaces-pour-progresser-la-memorisation-active", "title": "Stratégies efficaces pour progresser la mémorisation active"},
    {"slug": "strategies-efficaces-pour-progresser-la-motivation", "title": "Stratégies efficaces pour progresser la motivation"},
    {"slug": "strategies-efficaces-pour-progresser-la-planification-de-session", "title": "Stratégies efficaces pour progresser la planification de session"},
    {"slug": "strategies-efficaces-pour-progresser-la-prise-de-notes", "title": "Stratégies efficaces pour progresser la prise de notes"},
    {"slug": "strategies-efficaces-pour-progresser-la-resolution-de-problemes", "title": "Stratégies efficaces pour progresser la résolution de problèmes"},
    {"slug": "strategies-efficaces-pour-progresser-lanalyse-financiere", "title": "Stratégies efficaces pour progresser l'analyse financière"},
    {"slug": "strategies-efficaces-pour-progresser-le-management", "title": "Stratégies efficaces pour progresser le management"},
    {"slug": "strategies-efficaces-pour-progresser-le-raisonnement-logique", "title": "Stratégies efficaces pour progresser le raisonnement logique"},
    {"slug": "strategies-efficaces-pour-progresser-les-presentations-orales", "title": "Stratégies efficaces pour progresser les présentations orales"},
    {"slug": "strategies-efficaces-pour-progresser-les-revisions", "title": "Stratégies efficaces pour progresser les révisions"},
    {"slug": "strategies-efficaces-pour-progresser-lorganisation-personnelle", "title": "Stratégies efficaces pour progresser l'organisation personnelle"},
    {"slug": "strategies-efficaces-pour-progresser-notion", "title": "Stratégies efficaces pour progresser Notion"},
    {"slug": "techniques-avancees-pour-reussir-excel", "title": "Techniques avancées pour réussir Excel"},
    {"slug": "techniques-avancees-pour-reussir-la-comprehension-des-textes-complexes", "title": "Techniques avancées pour réussir la compréhension des textes complexes"},
    {"slug": "techniques-avancees-pour-reussir-la-comptabilite", "title": "Techniques avancées pour réussir la comptabilité"},
    {"slug": "techniques-avancees-pour-reussir-la-concentration", "title": "Techniques avancées pour réussir la concentration"},
    {"slug": "techniques-avancees-pour-reussir-la-lecture-academique", "title": "Techniques avancées pour réussir la lecture académique"},
    {"slug": "techniques-avancees-pour-reussir-la-motivation", "title": "Techniques avancées pour réussir la motivation"},
    {"slug": "techniques-avancees-pour-reussir-la-planification-de-session", "title": "Techniques avancées pour réussir la planification de session"},
    {"slug": "techniques-avancees-pour-reussir-la-prise-de-notes", "title": "Techniques avancées pour réussir la prise de notes"},
    {"slug": "techniques-avancees-pour-reussir-la-resolution-de-problemes", "title": "Techniques avancées pour réussir la résolution de problèmes"},
    {"slug": "techniques-avancees-pour-reussir-lanalyse-financiere", "title": "Techniques avancées pour réussir l'analyse financière"},
    {"slug": "techniques-avancees-pour-reussir-le-management", "title": "Techniques avancées pour réussir le management"},
    {"slug": "techniques-avancees-pour-reussir-le-marketing", "title": "Techniques avancées pour réussir le marketing"},
    {"slug": "techniques-avancees-pour-reussir-le-raisonnement-logique", "title": "Techniques avancées pour réussir le raisonnement logique"},
    {"slug": "techniques-avancees-pour-reussir-letude-des-matieres-difficiles", "title": "Techniques avancées pour réussir l'étude des matières difficiles"},
    {"slug": "techniques-avancees-pour-reussir-notion", "title": "Techniques avancées pour réussir Notion"},
    {"slug": "techniques-modernes-pour-etudier-excel", "title": "Techniques modernes pour étudier Excel"},
    {"slug": "techniques-modernes-pour-etudier-la-comprehension-des-textes-complexes", "title": "Techniques modernes pour étudier la compréhension des textes complexes"},
    {"slug": "techniques-modernes-pour-etudier-la-gestion-du-temps", "title": "Techniques modernes pour étudier la gestion du temps"},
    {"slug": "techniques-modernes-pour-etudier-la-lecture-academique", "title": "Techniques modernes pour étudier la lecture académique"},
    {"slug": "techniques-modernes-pour-etudier-la-memorisation-active", "title": "Techniques modernes pour étudier la mémorisation active"},
    {"slug": "techniques-modernes-pour-etudier-la-methodologie-universitaire", "title": "Techniques modernes pour étudier la méthodologie universitaire"},
    {"slug": "techniques-modernes-pour-etudier-la-motivation", "title": "Techniques modernes pour étudier la motivation"},
    {"slug": "techniques-modernes-pour-etudier-la-prise-de-notes", "title": "Techniques modernes pour étudier la prise de notes"},
    {"slug": "techniques-modernes-pour-etudier-le-sommeil-etudiant", "title": "Techniques modernes pour étudier le sommeil étudiant"},
    {"slug": "techniques-modernes-pour-etudier-les-examens-difficiles", "title": "Techniques modernes pour étudier les examens difficiles"},
    {"slug": "techniques-modernes-pour-etudier-les-presentations-orales", "title": "Techniques modernes pour étudier les présentations orales"},
    {"slug": "techniques-modernes-pour-etudier-les-strategies-dexamen", "title": "Techniques modernes pour étudier les stratégies d'examen"},
    {"slug": "techniques-modernes-pour-etudier-notion", "title": "Techniques modernes pour étudier Notion"}
]

def escape_sql_string(text):
    """Escape single quotes for SQL."""
    if not text:
        return "''"
    return text.replace("'", "''")

# Load outlines
print("Loading outlines from JSON...")
with open('scripts/articles/extracted_outlines.json', 'r', encoding='utf-8') as f:
    outlines_data = json.load(f)

# Create outlines dictionary
outlines_dict = {}
for item in outlines_data:
    title = item.get('title', '')
    outline = item.get('outline', '')
    if title and outline:
        outlines_dict[title] = outline

print(f"Loaded {len(outlines_dict)} outlines")

# Match articles with outlines
matched = []
unmatched = []

for article in articles:
    title = article['title']
    slug = article['slug']
    
    outline = outlines_dict.get(title)
    if outline:
        matched.append({
            'slug': slug,
            'outline': outline
        })
    else:
        unmatched.append(title)

print(f"\nMatched: {len(matched)} articles")
print(f"Unmatched: {len(unmatched)} articles")

if unmatched:
    print("\nUnmatched articles:")
    for title in unmatched[:10]:  # Show first 10
        print(f"  - {title}")

if not matched:
    print("No matches found. Exiting.")
    sys.exit(1)

# Generate bulk UPDATE SQL in batches of 50
batch_size = 50
sql_batches = []

for i in range(0, len(matched), batch_size):
    batch = matched[i:i+batch_size]
    
    values_clauses = []
    for item in batch:
        slug = item['slug']
        outline = escape_sql_string(item['outline'])
        values_clauses.append(f"('{slug}', '{outline}')")
    
    values_sql = ',\n        '.join(values_clauses)
    
    sql = f"""UPDATE general_articles AS ga
SET draft_outline = v.outline::text,
    status = 'draft',
    updated_at = NOW()
FROM (VALUES
        {values_sql}
    ) AS v(slug, outline)
WHERE ga.slug = v.slug;"""
    
    sql_batches.append(sql)

# Save to file
output_file = 'scripts/articles/final_bulk_update_all.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("-- Bulk update all remaining articles with outlines\n")
    f.write(f"-- Total: {len(matched)} articles in {len(sql_batches)} batches\n\n")
    for i, sql in enumerate(sql_batches, 1):
        f.write(f"-- Batch {i}\n")
        f.write(sql)
        f.write("\n\n")

print(f"\nGenerated {len(sql_batches)} SQL batches")
print(f"SQL saved to: {output_file}")
print(f"\nReady to execute via MCP Supabase!")
