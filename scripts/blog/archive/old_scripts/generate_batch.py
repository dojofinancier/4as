#!/usr/bin/env python3
"""
Generate blog posts for a batch of courses.

Usage: This script will be called by the assistant with course data from MCP.
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

def process_batch(courses_data):
    """
    Process a batch of courses.
    
    Args:
        courses_data: List of dicts, each containing:
            - course: dict with slug, code, title_fr, institution, domain, active
            - website_description: str
            - ratings: list of professor rating dicts
    """
    results = []
    
    for i, course_info in enumerate(courses_data, 1):
        course = course_info['course']
        website_description = course_info['website_description']
        ratings = course_info.get('ratings', [])
        
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(courses_data)}: {course['code']} - {course['title_fr']}")
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
                results.append({
                    'success': True,
                    'course_code': course['code'],
                    'course_slug': course['slug'],
                    'result': result
                })
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
    
    return results

if __name__ == '__main__':
    print("Batch processing script ready")
    print("This will be called by the assistant with course data from MCP")

