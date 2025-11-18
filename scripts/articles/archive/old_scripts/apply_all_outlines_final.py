#!/usr/bin/env python3
"""
Final script to apply all outline updates to the database.
This script reads each batch file and prints the SQL for manual execution,
or can be modified to use a database connection.
"""

import os
import re
import sys

def clean_sql_content(content):
    """Remove comments and clean SQL content."""
    content = re.sub(r'--.*?\n', '', content)
    return content.strip()

def main():
    print("=" * 60)
    print("APPLYING ALL OUTLINE UPDATES (BATCHES 3-25)")
    print("=" * 60)
    print()
    
    total_batches = 0
    total_updates = 0
    
    for batch_num in range(3, 26):
        batch_file = f'scripts/articles/batch_{batch_num}_outlines.sql'
        if os.path.exists(batch_file):
            with open(batch_file, 'r', encoding='utf-8') as f:
                content = f.read()
            cleaned = clean_sql_content(content)
            
            # Count UPDATE statements
            update_count = len(re.findall(r'UPDATE general_articles SET', cleaned))
            total_batches += 1
            total_updates += update_count
            
            print(f"Batch {batch_num}: {update_count} UPDATE statements")
        else:
            print(f"Warning: {batch_file} not found")
    
    print()
    print("=" * 60)
    print(f"SUMMARY: {total_batches} batches, {total_updates} total UPDATE statements")
    print("=" * 60)
    print()
    print("All batch SQL files are ready in: scripts/articles/")
    print("The assistant will now execute these via MCP Supabase execute_sql")
    print("Processing will be done batch by batch for efficiency.")

if __name__ == '__main__':
    main()
