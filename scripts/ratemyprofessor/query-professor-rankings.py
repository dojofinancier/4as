#!/usr/bin/env python3
"""
Query Top/Bottom Professor Rankings for a Course.

This script queries the professor_ratings table to get top 5 and bottom 5 professors
for a specific course based on different metrics.
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

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_top_bottom_professors(course_slug: str, metric: str = 'overall_rating', top_n: int = 5) -> Dict[str, List[Dict]]:
    """
    Get top N and bottom N professors for a course by a specific metric.
    
    Args:
        course_slug: Course slug to filter by
        metric: 'overall_rating', 'difficulty_rating', or 'would_take_again'
        top_n: Number of top/bottom professors to return
    
    Returns:
        {'top': [professor_data], 'bottom': [professor_data]}
    """
    try:
        # Fetch all ratings for this course
        response = supabase.table('professor_ratings')\
            .select('*')\
            .eq('course_slug', course_slug)\
            .not_.is_(metric, 'null')\
            .execute()
        
        ratings = response.data if response.data else []
        
        if not ratings:
            return {'top': [], 'bottom': []}
        
        # Sort by metric (descending for overall_rating and would_take_again, ascending for difficulty)
        if metric == 'difficulty_rating':
            # Lower difficulty is better, so we sort ascending
            sorted_ratings = sorted(ratings, key=lambda x: x.get(metric) or 0)
        else:
            # Higher rating is better, so we sort descending
            sorted_ratings = sorted(ratings, key=lambda x: x.get(metric) or 0, reverse=True)
        
        # Get top N and bottom N
        top = sorted_ratings[:top_n]
        bottom = sorted_ratings[-top_n:] if len(sorted_ratings) >= top_n else sorted_ratings
        
        # Reverse bottom list to show worst first
        bottom = list(reversed(bottom))
        
        return {'top': top, 'bottom': bottom}
        
    except Exception as e:
        print(f"Error getting top/bottom professors: {e}")
        return {'top': [], 'bottom': []}


def print_rankings(course_slug: str, metric: str, top_n: int = 5):
    """Print formatted rankings for a course."""
    results = get_top_bottom_professors(course_slug, metric, top_n)
    
    metric_labels = {
        'overall_rating': 'Overall Rating',
        'difficulty_rating': 'Difficulty Rating',
        'would_take_again': 'Would Take Again'
    }
    
    label = metric_labels.get(metric, metric)
    
    print(f"\n{'='*60}")
    print(f"Course: {course_slug}")
    print(f"Metric: {label}")
    print(f"{'='*60}\n")
    
    # Print top N
    print(f"TOP {top_n}:")
    print("-" * 60)
    if results['top']:
        for i, prof in enumerate(results['top'], 1):
            rating = prof.get(metric, 'N/A')
            name = prof.get('professor_name', 'Unknown')
            total_ratings = prof.get('total_ratings', 0)
            print(f"{i}. {name}")
            print(f"   {label}: {rating}")
            print(f"   Total Ratings: {total_ratings}")
            print()
    else:
        print("No data available")
        print()
    
    # Print bottom N
    print(f"BOTTOM {top_n}:")
    print("-" * 60)
    if results['bottom']:
        for i, prof in enumerate(results['bottom'], 1):
            rating = prof.get(metric, 'N/A')
            name = prof.get('professor_name', 'Unknown')
            total_ratings = prof.get('total_ratings', 0)
            print(f"{i}. {name}")
            print(f"   {label}: {rating}")
            print(f"   Total Ratings: {total_ratings}")
            print()
    else:
        print("No data available")
        print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Query top/bottom professor rankings for a course',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get top 5 and bottom 5 by overall rating
  python query-professor-rankings.py fin5521 --metric overall_rating

  # Get top 10 and bottom 10 by difficulty
  python query-professor-rankings.py fin5521 --metric difficulty_rating --top-n 10

  # Get all metrics for a course
  python query-professor-rankings.py fin5521 --all-metrics
        """
    )
    
    parser.add_argument('course_slug', help='Course slug (e.g., fin5521)')
    parser.add_argument('--metric', choices=['overall_rating', 'difficulty_rating', 'would_take_again'],
                       default='overall_rating', help='Metric to rank by (default: overall_rating)')
    parser.add_argument('--top-n', type=int, default=5, help='Number of top/bottom professors to show (default: 5)')
    parser.add_argument('--all-metrics', action='store_true', 
                       help='Show rankings for all metrics')
    
    args = parser.parse_args()
    
    if args.all_metrics:
        for metric in ['overall_rating', 'difficulty_rating', 'would_take_again']:
            print_rankings(args.course_slug, metric, args.top_n)
    else:
        print_rankings(args.course_slug, args.metric, args.top_n)


if __name__ == '__main__':
    main()

