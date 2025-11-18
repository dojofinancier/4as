#!/usr/bin/env python3
"""
Apply all generated outline SQL files to the database.
This script reads all batch SQL files and executes them via MCP Supabase.
"""

import os
import re
import glob

def extract_sql_statements(sql_file):
    """Extract individual UPDATE statements from SQL file."""
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by UPDATE statements
    statements = re.split(r'(UPDATE general_articles SET)', content)
    updates = []
    
    for i in range(1, len(statements), 2):
        if i + 1 < len(statements):
            full_statement = statements[i] + statements[i + 1]
            # Remove trailing semicolons and whitespace
            full_statement = full_statement.strip().rstrip(';').strip()
            if full_statement:
                updates.append(full_statement + ';')
    
    return updates

def main():
    # Get all batch SQL files (batches 3-25, since 1-2 were already applied)
    sql_files = sorted(glob.glob('scripts/articles/batch_*_outlines.sql'))
    
    # Filter to batches 3-25
    batch_files = [f for f in sql_files if any(f'batch_{i}_outlines.sql' in f for i in range(3, 26))]
    
    print(f"Found {len(batch_files)} batch files to process (batches 3-25)")
    print("="*60)
    
    total_statements = 0
    for sql_file in batch_files:
        batch_num = re.search(r'batch_(\d+)_outlines', sql_file).group(1)
        print(f"\nProcessing batch {batch_num}...")
        
        statements = extract_sql_statements(sql_file)
        print(f"  Found {len(statements)} UPDATE statements")
        
        # Save individual statements for execution
        for i, stmt in enumerate(statements, 1):
            output_file = f'scripts/articles/batch{batch_num}_update_{i}.sql'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(stmt)
            total_statements += 1
    
    print(f"\n{'='*60}")
    print(f"Total: {total_statements} UPDATE statements prepared")
    print(f"Individual SQL files created in scripts/articles/")
    print(f"The assistant will now execute these via MCP Supabase")

if __name__ == '__main__':
    main()

