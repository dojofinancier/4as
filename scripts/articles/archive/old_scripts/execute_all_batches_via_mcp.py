#!/usr/bin/env python3
"""
Script to help execute all batch SQL files via MCP Supabase.
This script reads each batch file and provides instructions for execution.
"""

import os
import re

def clean_sql_content(content):
    """Remove comments and clean SQL content."""
    content = re.sub(r'--.*?\n', '', content)
    return content.strip()

print("=" * 60)
print("BATCH SQL FILES READY FOR EXECUTION")
print("=" * 60)
print()

for batch_num in range(3, 26):
    batch_file = f'scripts/articles/batch_{batch_num}_outlines.sql'
    execute_file = f'scripts/articles/batch_{batch_num}_execute.sql'
    
    if os.path.exists(batch_file):
        with open(batch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        cleaned = clean_sql_content(content)
        
        # Save cleaned version
        with open(execute_file, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        # Count UPDATE statements
        update_count = len(re.findall(r'UPDATE general_articles SET', cleaned))
        file_size = len(cleaned)
        
        print(f"Batch {batch_num}: {update_count} statements, {file_size:,} chars - {execute_file}")
    else:
        print(f"Warning: {batch_file} not found")

print()
print("=" * 60)
print("All batch SQL files have been prepared for execution.")
print("The assistant will now execute them via MCP Supabase execute_sql")
print("=" * 60)

