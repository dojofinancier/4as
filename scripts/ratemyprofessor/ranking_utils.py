#!/usr/bin/env python3
"""
Shared ranking utilities for professor ratings.
Uses MCP Supabase access (no environment variables needed).
"""

from typing import Dict, List, Optional, Tuple
import sys

# MCP Supabase tools are available via the assistant, but for standalone scripts
# we'll use direct SQL execution patterns that can be called via MCP
# This module provides the ranking logic that can be used by both MCP and direct scripts


def aggregate_professor_ratings(ratings: List[Dict]) -> Dict[str, Dict]:
    """
    Aggregate ratings by professor name across multiple courses.
    
    Args:
        ratings: List of rating dictionaries from professor_ratings table
    
    Returns:
        Dictionary mapping professor_name to aggregated data
    """
    professor_aggregates = {}
    
    for rating in ratings:
        prof_name = rating.get('professor_name', '')
        if not prof_name:
            continue
        
        if prof_name not in professor_aggregates:
            professor_aggregates[prof_name] = {
                'professor_name': prof_name,
                'overall_ratings': [],
                'difficulty_ratings': [],
                'would_take_again_ratings': [],
                'total_ratings': 0,
                'courses_count': 0,
                'course_slugs': set(),
                'professor_rmp_id': rating.get('professor_rmp_id'),
            }
        
        data = professor_aggregates[prof_name]
        
        # Collect rating values
        if rating.get('overall_rating') is not None:
            data['overall_ratings'].append(rating['overall_rating'])
        if rating.get('difficulty_rating') is not None:
            data['difficulty_ratings'].append(rating['difficulty_rating'])
        if rating.get('would_take_again') is not None:
            data['would_take_again_ratings'].append(rating['would_take_again'])
        
        data['total_ratings'] += rating.get('total_ratings', 0)
        data['courses_count'] += 1
        data['course_slugs'].add(rating.get('course_slug', ''))
    
    # Calculate averages
    for prof_name, data in professor_aggregates.items():
        data['avg_overall_rating'] = (
            sum(data['overall_ratings']) / len(data['overall_ratings'])
            if data['overall_ratings'] else None
        )
        data['avg_difficulty_rating'] = (
            sum(data['difficulty_ratings']) / len(data['difficulty_ratings'])
            if data['difficulty_ratings'] else None
        )
        data['avg_would_take_again'] = (
            sum(data['would_take_again_ratings']) / len(data['would_take_again_ratings'])
            if data['would_take_again_ratings'] else None
        )
        data['course_slugs'] = list(data['course_slugs'])
        # Remove raw lists to keep output clean
        del data['overall_ratings']
        del data['difficulty_ratings']
        del data['would_take_again_ratings']
    
    return professor_aggregates


def rank_professors(
    ratings: List[Dict],
    metric: str = 'overall_rating',
    top_n: int = 5,
    aggregate: bool = False
) -> Dict[str, List[Dict]]:
    """
    Rank professors by a specific metric.
    
    Args:
        ratings: List of rating dictionaries
        metric: 'overall_rating', 'difficulty_rating', or 'would_take_again'
        top_n: Number of top/bottom professors to return
        aggregate: If True, aggregate by professor name (for domain-level rankings)
    
    Returns:
        {'top': [professor_data], 'bottom': [professor_data]}
    """
    if not ratings:
        return {'top': [], 'bottom': []}
    
    if aggregate:
        # Aggregate by professor name
        professor_aggregates = aggregate_professor_ratings(ratings)
        professor_list = list(professor_aggregates.values())
        
        # Use aggregated average for ranking
        metric_key = f'avg_{metric}'
        
        # Filter out professors without the metric
        professor_list = [p for p in professor_list if p.get(metric_key) is not None]
        
        if not professor_list:
            return {'top': [], 'bottom': []}
        
        # Sort by metric
        if metric == 'difficulty_rating':
            # Lower difficulty is better
            sorted_profs = sorted(professor_list, key=lambda x: x.get(metric_key, float('inf')))
        else:
            # Higher rating is better
            sorted_profs = sorted(professor_list, key=lambda x: x.get(metric_key, 0), reverse=True)
    else:
        # Course-level: use individual ratings
        # Filter out ratings without the metric
        filtered_ratings = [r for r in ratings if r.get(metric) is not None]
        
        if not filtered_ratings:
            return {'top': [], 'bottom': []}
        
        # Sort by metric
        if metric == 'difficulty_rating':
            sorted_profs = sorted(filtered_ratings, key=lambda x: x.get(metric, float('inf')))
        else:
            sorted_profs = sorted(filtered_ratings, key=lambda x: x.get(metric, 0), reverse=True)
    
    # Get top N and bottom N
    top = sorted_profs[:top_n]
    bottom = sorted_profs[-top_n:] if len(sorted_profs) >= top_n else sorted_profs
    bottom = list(reversed(bottom))  # Reverse to show worst first
    
    return {'top': top, 'bottom': bottom}


def format_ranking_output(
    results: Dict[str, List[Dict]],
    metric: str,
    context: str = '',
    top_n: int = 5
) -> str:
    """
    Format ranking results for display.
    
    Args:
        results: {'top': [...], 'bottom': [...]}
        metric: Metric name
        context: Context string (e.g., course slug or domain name)
        top_n: Number of top/bottom
    
    Returns:
        Formatted string
    """
    metric_labels = {
        'overall_rating': 'Overall Rating',
        'difficulty_rating': 'Difficulty Rating (Lower is Better)',
        'would_take_again': 'Would Take Again'
    }
    
    label = metric_labels.get(metric, metric)
    output = []
    
    if context:
        output.append(f"\n{'='*80}")
        output.append(f"{context}")
        output.append(f"Metric: {label}")
        output.append(f"{'='*80}\n")
    
    # Top N
    output.append(f"TOP {top_n}:")
    output.append("-" * 80)
    if results['top']:
        for i, prof in enumerate(results['top'], 1):
            if 'avg_' + metric in prof:
                # Aggregated ranking
                value = prof.get('avg_' + metric, 'N/A')
                name = prof.get('professor_name', 'Unknown')
                total_ratings = prof.get('total_ratings', 0)
                courses_count = prof.get('courses_count', 0)
                output.append(f"{i}. {name}")
                output.append(f"   Average {label}: {value:.2f}" if isinstance(value, (int, float)) else f"   Average {label}: {value}")
                output.append(f"   Total Ratings: {total_ratings}")
                output.append(f"   Teaches {courses_count} course(s)")
            else:
                # Course-level ranking
                value = prof.get(metric, 'N/A')
                name = prof.get('professor_name', 'Unknown')
                total_ratings = prof.get('total_ratings', 0)
                output.append(f"{i}. {name}")
                output.append(f"   {label}: {value}")
                output.append(f"   Total Ratings: {total_ratings}")
            output.append("")
    else:
        output.append("No data available")
        output.append("")
    
    # Bottom N
    output.append(f"BOTTOM {top_n}:")
    output.append("-" * 80)
    if results['bottom']:
        for i, prof in enumerate(results['bottom'], 1):
            if 'avg_' + metric in prof:
                # Aggregated ranking
                value = prof.get('avg_' + metric, 'N/A')
                name = prof.get('professor_name', 'Unknown')
                total_ratings = prof.get('total_ratings', 0)
                courses_count = prof.get('courses_count', 0)
                output.append(f"{i}. {name}")
                output.append(f"   Average {label}: {value:.2f}" if isinstance(value, (int, float)) else f"   Average {label}: {value}")
                output.append(f"   Total Ratings: {total_ratings}")
                output.append(f"   Teaches {courses_count} course(s)")
            else:
                # Course-level ranking
                value = prof.get(metric, 'N/A')
                name = prof.get('professor_name', 'Unknown')
                total_ratings = prof.get('total_ratings', 0)
                output.append(f"{i}. {name}")
                output.append(f"   {label}: {value}")
                output.append(f"   Total Ratings: {total_ratings}")
            output.append("")
    else:
        output.append("No data available")
        output.append("")
    
    return "\n".join(output)

