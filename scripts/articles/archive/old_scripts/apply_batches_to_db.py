#!/usr/bin/env python3
"""
Read batch SQL files and prepare them for execution.
This script will extract UPDATE statements from each batch file.
"""

import re
import os

def extract_updates_from_file(filepath):
    """Extract individual UPDATE statements from a batch SQL file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments
    content = re.sub(r'--.*?\n', '', content)
    
    # Split by UPDATE statements - look for pattern: UPDATE general_articles SET
    # We need to match the full UPDATE statement including the WHERE clause
    # Each UPDATE statement ends with a semicolon followed by whitespace/newline
    statements = []
    
    # Find all UPDATE statements
    pattern = r'UPDATE general_articles SET.*?WHERE slug = [^;]+;'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        statements.append(match.strip())
    
    return statements

# Process batches 3-25
all_statements = []
for batch_num in range(3, 26):
    batch_file = f'scripts/articles/batch_{batch_num}_outlines.sql'
    if os.path.exists(batch_file):
        statements = extract_updates_from_file(batch_file)
        all_statements.extend(statements)
        print(f"Batch {batch_num}: {len(statements)} statements")
    else:
        print(f"Warning: {batch_file} not found")

print(f"\nTotal: {len(all_statements)} UPDATE statements ready to execute")
print("The assistant will now execute these via MCP Supabase")

# Save individual statements for reference
for i, stmt in enumerate(all_statements, 1):
    output_file = f'scripts/articles/update_statement_{i}.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(stmt)
    
    if i <= 5 or i > len(all_statements) - 5:
        print(f"Saved: {output_file}")

print(f"\nAll {len(all_statements)} statements saved as individual files")
print("Ready for batch execution via MCP Supabase")
