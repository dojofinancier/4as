#!/usr/bin/env python3
"""
Apply all batch SQL files to database via migrations.
This script reads each batch SQL file and applies it as a migration.
"""

import os
import re
import glob

def read_batch_sql_file(sql_file):
    """Read a batch SQL file and return its content."""
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove comments
    content = re.sub(r'^--.*$', '', content, flags=re.MULTILINE)
    return content.strip()

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
    
    print(f"Found {len(batch_files)} batch files to process (batches 3-25)")
    print("="*60)
    
    for batch_num, sql_file in batch_files:
        print(f"\nProcessing batch {batch_num}...")
        sql_content = read_batch_sql_file(sql_file)
        
        # Save to a migration file
        migration_file = f'scripts/articles/migration_batch_{batch_num}.sql'
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Migration for batch {batch_num}\n\n")
            f.write(sql_content)
        
        print(f"  Saved migration file: {migration_file}")
        print(f"  SQL content length: {len(sql_content)} characters")
        print(f"  Ready for execution via MCP Supabase apply_migration")
    
    print(f"\n{'='*60}")
    print(f"All {len(batch_files)} migration files created")
    print("The assistant will now execute them via MCP Supabase")

if __name__ == '__main__':
    main()

