#!/usr/bin/env python3
"""
Apply all batch outline updates to the database.
This script reads all batch SQL files and applies them via MCP Supabase.
"""

import re
import os
import sys

def split_sql_statements(sql_content: str) -> list:
    """Split SQL content into individual UPDATE statements."""
    # Remove comments
    sql_content = re.sub(r'--.*?\n', '', sql_content)
    # Split by UPDATE statements
    statements = re.split(r'(?=UPDATE general_articles SET)', sql_content)
    # Filter out empty strings
    statements = [s.strip() for s in statements if s.strip() and s.strip().startswith('UPDATE')]
    return statements

def main():
    # Process batches 3-25 (batches 1-2 already applied)
    batch_files = []
    for i in range(3, 26):
        batch_file = f'scripts/articles/batch_{i}_outlines.sql'
        if os.path.exists(batch_file):
            batch_files.append(batch_file)
        else:
            print(f"Warning: {batch_file} not found")
    
    print(f"Found {len(batch_files)} batch files to process")
    print("SQL statements ready to execute via MCP Supabase")
    print("\nThe assistant will now execute these statements batch by batch.")
    
    # Count total statements
    total_statements = 0
    for batch_file in batch_files:
        with open(batch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        statements = split_sql_statements(content)
        total_statements += len(statements)
        print(f"{batch_file}: {len(statements)} statements")
    
    print(f"\nTotal: {total_statements} UPDATE statements to execute")

if __name__ == '__main__':
    main()

