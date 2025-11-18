#!/usr/bin/env python3
"""
Fetch Professor Ratings from RateMyProfessor and store in Supabase.

This script:
1. Fetches all active courses from Supabase
2. For each course, finds professors by matching institution and domain/department
3. Stores professor ratings in the professor_ratings table
"""

import os
import sys
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

try:
    import ratemyprofessor
except ImportError:
    print("Error: RateMyProfessorAPI not installed. Run: pip install RateMyProfessorAPI")
    sys.exit(1)

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase-py not installed. Run: pip install supabase")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('professor_ratings_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    logger.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Mapping of domain names to RateMyProfessor department names
# This may need adjustment based on actual RateMyProfessor department names
DOMAIN_TO_DEPARTMENT = {
    'Finance': ['Finance', 'Financial', 'Finances'],
    'Comptabilité': ['Accounting', 'Comptabilité', 'Accountancy'],
    'Mathématiques': ['Mathematics', 'Math', 'Mathématiques'],
    # Add more mappings as needed
}

# Rate limiting: wait between API calls to avoid being blocked
RATE_LIMIT_DELAY = 1  # seconds between API calls


def normalize_institution_name(institution: str) -> str:
    """
    Normalize institution name to match RateMyProfessor format.
    Example: "ESG-UQAM" -> "ESG UQAM" or "UQAM"
    """
    # Common mappings for Quebec universities
    institution_mappings = {
        'ESG-UQAM': 'UQAM',
        'HEC Montréal': 'HEC Montreal',
        'Université Laval': 'Université Laval',
        'Université Sherbrooke': 'Université de Sherbrooke',
        'Téluq': 'TELUQ',
        # Add more mappings as needed
    }
    return institution_mappings.get(institution, institution)


def get_department_keywords(domain: str) -> List[str]:
    """Get possible department names for a domain."""
    return DOMAIN_TO_DEPARTMENT.get(domain, [domain])


def load_professor_mapping(csv_path: str = 'scripts/professor_mapping.csv') -> Dict[tuple, List[str]]:
    """
    Load professor mapping from CSV file.
    Expected format: domain,professor_name,institution
    Returns: {(institution, domain): [professor_names]}
    """
    mapping = {}
    
    if not os.path.exists(csv_path):
        logger.warning(f"Professor mapping file not found: {csv_path}")
        logger.info("Create a CSV file with format: domain,professor_name,institution")
        return mapping
    
    try:
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Skip comment lines
            lines = [line for line in f if not line.strip().startswith('#')]
            f.seek(0)
            
            reader = csv.DictReader(f)
            for row in reader:
                domain = row.get('domain', '').strip()
                professor_name = row.get('professor_name', '').strip()
                institution = row.get('institution', '').strip()
                
                if domain and professor_name:
                    key = (institution, domain)
                    if key not in mapping:
                        mapping[key] = []
                    mapping[key].append(professor_name)
        
        total_professors = sum(len(v) for v in mapping.values())
        logger.info(f"Loaded {total_professors} professor mappings across {len(mapping)} domain-institution combinations from {csv_path}")
    except Exception as e:
        logger.error(f"Error loading professor mapping: {e}")
    
    return mapping


def find_professor_by_name(school, professor_name: str) -> Optional[Dict]:
    """
    Search for a professor by name in a school.
    
    Returns professor data dictionary or None if not found.
    """
    try:
        professor = ratemyprofessor.get_professor_by_school_and_name(school, professor_name)
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        
        if not professor:
            return None
        
        # Extract professor data
        professor_data = {
            'name': professor.name,
            'id': getattr(professor, 'id', None),
            'rating': professor.rating if hasattr(professor, 'rating') else None,
            'difficulty': professor.difficulty if hasattr(professor, 'difficulty') else None,
            'would_take_again': professor.would_take_again if hasattr(professor, 'would_take_again') else None,
            'num_ratings': professor.num_ratings if hasattr(professor, 'num_ratings') else 0,
            'department': professor.department if hasattr(professor, 'department') else None,
        }
        
        return professor_data
        
    except Exception as e:
        logger.error(f"    Error searching for professor '{professor_name}': {e}")
        return None


def find_professors_for_domain(domain: str, institution: str, school, professor_mapping: Dict[tuple, List[str]]) -> List[Dict]:
    """
    Find professors for a domain/institution combination using the mapping file.
    
    Returns list of professor data dictionaries.
    """
    professors = []
    
    if not school:
        return professors
    
    # Get professor names for this domain-institution combination
    key = (institution, domain)
    professor_names = professor_mapping.get(key, [])
    
    if not professor_names:
        logger.info(f"  No professor mapping found for domain '{domain}' at '{institution}'")
        return professors
    
    logger.info(f"  Searching for {len(professor_names)} professor(s) in domain '{domain}'")
    
    # Search for each professor
    for professor_name in professor_names:
        logger.info(f"    Searching: {professor_name}")
        professor_data = find_professor_by_name(school, professor_name)
        
        if professor_data:
            professors.append(professor_data)
            logger.info(f"    ✓ Found: {professor_data['name']} (Rating: {professor_data.get('rating', 'N/A')}/5.0)")
        else:
            logger.warning(f"    ✗ Not found: {professor_name}")
    
    return professors


def store_professor_rating(course_slug: str, professor_data: Dict) -> bool:
    """
    Store or update professor rating in Supabase.
    
    Returns True if successful, False otherwise.
    """
    try:
        # Prepare data for insertion
        rating_data = {
            'course_slug': course_slug,
            'professor_name': professor_data.get('name', ''),
            'professor_rmp_id': professor_data.get('id'),
            'overall_rating': professor_data.get('rating'),
            'difficulty_rating': professor_data.get('difficulty'),
            'would_take_again': professor_data.get('would_take_again'),
            'total_ratings': professor_data.get('num_ratings', 0),
            'last_updated': datetime.utcnow().isoformat(),
        }
        
        # Upsert (insert or update) the rating
        # Using upsert with unique constraint on (course_slug, professor_name)
        result = supabase.table('professor_ratings').upsert(
            rating_data,
            on_conflict='course_slug,professor_name'
        ).execute()
        
        logger.info(f"    ✓ Stored rating for {professor_data.get('name')}")
        return True
        
    except Exception as e:
        logger.error(f"    ✗ Error storing rating for {professor_data.get('name')}: {e}")
        return False


def process_domain_group(domain: str, institution: str, courses: List[Dict], professor_mapping: Dict[tuple, List[str]]) -> Dict:
    """
    Process all courses in a domain: find professors and map them to all courses.
    
    Returns statistics dictionary.
    """
    stats = {
        'domain': domain,
        'institution': institution,
        'courses_count': len(courses),
        'school_found': False,
        'professors_found': 0,
        'ratings_stored': 0,
        'errors': []
    }
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing domain: '{domain}' at '{institution}'")
    logger.info(f"  Courses in this domain: {len(courses)}")
    logger.info(f"  Course codes: {', '.join([c.get('code', '') for c in courses])}")
    
    # Normalize institution name
    normalized_institution = normalize_institution_name(institution)
    
    # Find school on RateMyProfessor
    try:
        school = ratemyprofessor.get_school_by_name(normalized_institution)
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        
        if not school:
            logger.warning(f"  ✗ School '{normalized_institution}' not found on RateMyProfessor")
            stats['errors'].append(f"School not found: {normalized_institution}")
            return stats
        
        stats['school_found'] = True
        logger.info(f"  ✓ Found school: {school.name}")
        
    except Exception as e:
        logger.error(f"  ✗ Error finding school: {e}")
        stats['errors'].append(f"Error finding school: {e}")
        return stats
    
    # Find professors for this domain
    try:
        professors = find_professors_for_domain(domain, institution, school, professor_mapping)
        stats['professors_found'] = len(professors)
        
        if not professors:
            logger.warning(f"  No professors found for domain '{domain}'")
            return stats
        
        logger.info(f"  Found {len(professors)} professor(s), mapping to {len(courses)} course(s)")
        
        # Map each professor to all courses in this domain
        for course in courses:
            course_slug = course.get('slug', '')
            course_code = course.get('code', '')
            
            if not course_slug:
                continue
            
            logger.info(f"  Mapping professors to course: {course_code}")
            
            # Store ratings for each professor for this course
            for professor_data in professors:
                if store_professor_rating(course_slug, professor_data):
                    stats['ratings_stored'] += 1
                time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
            
    except Exception as e:
        logger.error(f"  ✗ Error processing professors: {e}")
        stats['errors'].append(f"Error processing professors: {e}")
    
    return stats


def group_courses_by_domain(courses: List[Dict]) -> Dict[tuple, List[Dict]]:
    """
    Group courses by (institution, domain) combination.
    
    Returns: {(institution, domain): [courses]}
    """
    grouped = {}
    
    for course in courses:
        institution = course.get('institution', '') or ''
        domain = course.get('domain', '') or ''
        
        if not domain:
            logger.warning(f"Course {course.get('code', '')} has no domain, skipping")
            continue
        
        key = (institution, domain)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(course)
    
    return grouped


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
        logger.error(f"Error getting top/bottom professors: {e}")
        return {'top': [], 'bottom': []}


def main():
    """Main function to fetch and store professor ratings."""
    logger.info("=" * 60)
    logger.info("Starting Professor Ratings Fetch (Domain-Based)")
    logger.info("=" * 60)
    
    # Load professor mapping from CSV
    professor_mapping = load_professor_mapping()
    
    if not professor_mapping:
        logger.warning("No professor mapping found. Create scripts/professor_mapping.csv")
        logger.info("Format: domain,professor_name,institution")
        logger.info("Example: Finance,John Smith,ESG-UQAM")
        logger.warning("Exiting. Create the mapping file and try again.")
        logger.info("You can create an empty CSV file to continue, but no professors will be found.")
        return
    
    # Fetch all active courses
    try:
        response = supabase.table('courses').select('*').eq('active', True).execute()
        courses = response.data if response.data else []
        logger.info(f"Found {len(courses)} active courses")
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        sys.exit(1)
    
    if not courses:
        logger.warning("No active courses found")
        return
    
    # Group courses by (institution, domain)
    grouped_courses = group_courses_by_domain(courses)
    logger.info(f"Grouped into {len(grouped_courses)} domain-institution combinations")
    
    # Process each domain group
    all_stats = []
    for i, ((institution, domain), domain_courses) in enumerate(grouped_courses.items(), 1):
        logger.info(f"\n[{i}/{len(grouped_courses)}]")
        stats = process_domain_group(domain, institution, domain_courses, professor_mapping)
        all_stats.append(stats)
        
        # Rate limiting between domain groups
        if i < len(grouped_courses):
            time.sleep(RATE_LIMIT_DELAY)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("Summary")
    logger.info("=" * 60)
    
    total_domains = len(all_stats)
    domains_with_schools = sum(1 for s in all_stats if s['school_found'])
    total_professors = sum(s['professors_found'] for s in all_stats)
    total_ratings = sum(s['ratings_stored'] for s in all_stats)
    total_courses = sum(s['courses_count'] for s in all_stats)
    
    logger.info(f"Total domain-institution combinations: {total_domains}")
    logger.info(f"Total courses processed: {total_courses}")
    logger.info(f"Schools found: {domains_with_schools}")
    logger.info(f"Professors found: {total_professors}")
    logger.info(f"Ratings stored: {total_ratings}")
    
    # Log domains with errors
    domains_with_errors = [s for s in all_stats if s['errors']]
    if domains_with_errors:
        logger.warning(f"\nDomains with errors: {len(domains_with_errors)}")
        for stats in domains_with_errors:
            logger.warning(f"  {stats['domain']} at {stats['institution']}: {', '.join(stats['errors'])}")
    
    logger.info("\nDone!")


if __name__ == '__main__':
    main()

