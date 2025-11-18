#!/usr/bin/env python3
"""
Generate Top/Bottom Professor Rankings by Domain/Institution.

This script generates rankings for all courses in a domain/institution combination,
showing top 5 and bottom 5 professors for each metric.

Uses MCP Supabase access - no environment variables needed when run via assistant.
For standalone use, requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
"""

import os
import sys
import argparse
from typing import Dict, List
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase-py not installed. Run: pip install supabase")
    sys.exit(1)

# Import ranking utilities
from ranking_utils import rank_professors, format_ranking_output

# Load environment variables (optional - for standalone use)
load_dotenv()

# Supabase configuration (optional - for standalone use)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Initialize Supabase client (only if env vars are available)
supabase: Client = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_top_bottom_professors_by_domain(
    domain: str,
    institution: str,
    metric: str = 'overall_rating',
    top_n: int = 5,
    ratings_data: List[Dict] = None
) -> Dict[str, List[Dict]]:
    """
    Get top N and bottom N professors for a domain/institution by a specific metric.
    
    Args:
        domain: Domain name
        institution: Institution name
        metric: 'overall_rating', 'difficulty_rating', or 'would_take_again'
        top_n: Number of top/bottom professors to return
        ratings_data: Optional pre-fetched ratings data (for MCP use)
    
    Returns:
        {'top': [professor_data], 'bottom': [professor_data], 'courses': [course_info]}
    """
    try:
        courses = []
        
        if supabase:
            # Standalone mode: fetch from Supabase
            courses_response = supabase.table('courses')\
                .select('slug, code, title_fr')\
                .eq('active', True)\
                .eq('domain', domain)\
                .eq('institution', institution)\
                .execute()
            
            courses = courses_response.data if courses_response.data else []
            
            if not courses:
                return {'top': [], 'bottom': [], 'courses': []}
            
            course_slugs = [c['slug'] for c in courses if c.get('slug')]
            
            if not course_slugs:
                return {'top': [], 'bottom': [], 'courses': courses}
            
            # Fetch all ratings for courses in this domain
            response = supabase.table('professor_ratings')\
                .select('*')\
                .in_('course_slug', course_slugs)\
                .not_.is_(metric, 'null')\
                .execute()
            
            ratings = response.data if response.data else []
        else:
            # MCP mode: use provided ratings_data
            if ratings_data is None:
                return {'top': [], 'bottom': [], 'courses': []}
            ratings = ratings_data
        
        if not ratings:
            return {'top': [], 'bottom': [], 'courses': courses}
        
        # Use ranking utility with aggregation
        results = rank_professors(ratings, metric=metric, top_n=top_n, aggregate=True)
        results['courses'] = courses
        
        return results
        
    except Exception as e:
        print(f"Error getting rankings: {e}")
        import traceback
        traceback.print_exc()
        return {'top': [], 'bottom': [], 'courses': []}


def print_domain_rankings(domain: str, institution: str, metric: str, top_n: int = 5):
    """Print formatted rankings for a domain/institution."""
    results = get_top_bottom_professors_by_domain(domain, institution, metric, top_n)
    
    context = f"Domain: {domain} | Institution: {institution}\nTotal Courses: {len(results['courses'])}"
    output = format_ranking_output(results, metric, context, top_n)
    print(output)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate top/bottom professor rankings by domain/institution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get top 5 and bottom 5 by overall rating for Finance at ESG-UQAM
  python generate-domain-rankings.py Finance ESG-UQAM --metric overall_rating

  # Get top 10 and bottom 10 by difficulty for all domains
  python generate-domain-rankings.py --all-domains --metric difficulty_rating --top-n 10

  # Get all metrics for a specific domain
  python generate-domain-rankings.py Finance ESG-UQAM --all-metrics
        """
    )
    
    parser.add_argument('domain', nargs='?', help='Domain name (e.g., Finance, Comptabilité)')
    parser.add_argument('institution', nargs='?', help='Institution name (e.g., ESG-UQAM)')
    parser.add_argument('--metric', choices=['overall_rating', 'difficulty_rating', 'would_take_again'],
                       default='overall_rating', help='Metric to rank by (default: overall_rating)')
    parser.add_argument('--top-n', type=int, default=5, help='Number of top/bottom professors to show (default: 5)')
    parser.add_argument('--all-metrics', action='store_true', 
                       help='Show rankings for all metrics')
    parser.add_argument('--all-domains', action='store_true',
                       help='Show rankings for all domain/institution combinations')
    
    args = parser.parse_args()
    
    if args.all_domains:
        # Get all unique domain/institution combinations
        try:
            response = supabase.table('courses')\
                .select('domain, institution')\
                .eq('active', True)\
                .not_.is_('domain', 'null')\
                .not_.is_('institution', 'null')\
                .execute()
            
            courses = response.data if response.data else []
            domain_institutions = set()
            for course in courses:
                domain = course.get('domain')
                institution = course.get('institution')
                if domain and institution:
                    domain_institutions.add((domain, institution))
            
            for domain, institution in sorted(domain_institutions):
                if args.all_metrics:
                    for metric in ['overall_rating', 'difficulty_rating', 'would_take_again']:
                        print_domain_rankings(domain, institution, metric, args.top_n)
                else:
                    print_domain_rankings(domain, institution, args.metric, args.top_n)
        except Exception as e:
            print(f"Error fetching domains: {e}")
            sys.exit(1)
    elif args.domain and args.institution:
        if args.all_metrics:
            for metric in ['overall_rating', 'difficulty_rating', 'would_take_again']:
                print_domain_rankings(args.domain, args.institution, metric, args.top_n)
        else:
            print_domain_rankings(args.domain, args.institution, args.metric, args.top_n)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

