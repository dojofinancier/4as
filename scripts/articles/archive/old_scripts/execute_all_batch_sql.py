#!/usr/bin/env python3
"""
Read batch SQL files and execute all UPDATE statements.
This script processes batches 3-25 and executes all SQL statements.
"""

import os
import re
import glob

def extract_sql_statements(sql_file):
    """Extract all UPDATE statements from a batch SQL file."""
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments
    content = re.sub(r'^--.*$', '', content, flags=re.MULTILINE)
    
    # Split by UPDATE statements
    # Pattern: UPDATE general_articles SET ... WHERE slug = '...';
    pattern = r"(UPDATE general_articles SET.*?WHERE slug = '[^']+';)"
    statements = re.findall(pattern, content, re.DOTALL)
    
    return statements

def main():
    # Get all batch SQL files (batches 3-25)
    sql_files = sorted(glob.glob('scripts/articles/batch_*_outlines.sql'))
    
    # Filter to batches 3-25
    batch_files = []
    for f in sql_files:
        match = re.search(r'batch_(\d+)_outlines', f)
        if match:
            batch_num = int(match.group(1))
            if 3 <= batch_num <= 25:
                batch_files.append((batch_num, f))
    
    batch_files.sort(key=lambda x: x[0])
    
    print(f"Processing {len(batch_files)} batch files (batches 3-25)")
    print("="*60)
    
    all_statements = []
    for batch_num, sql_file in batch_files:
        print(f"Reading batch {batch_num}...")
        statements = extract_sql_statements(sql_file)
        print(f"  Found {len(statements)} UPDATE statements")
        all_statements.extend(statements)
    
    print(f"\n{'='*60}")
    print(f"Total: {len(all_statements)} UPDATE statements ready")
    print("SQL statements will be executed via MCP Supabase")
    print("The assistant will execute them in groups")

if __name__ == '__main__':
    main()

