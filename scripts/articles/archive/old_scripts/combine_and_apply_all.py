#!/usr/bin/env python3
"""
Combine all batch SQL files and prepare for execution.
This script reads all batch files (3-25) and combines them into a single SQL file.
"""

import os
import re

def clean_sql_content(content):
    """Remove comments and clean SQL content."""
    # Remove SQL comments
    content = re.sub(r'--.*?\n', '', content)
    # Remove empty lines
    lines = [line for line in content.split('\n') if line.strip()]
    return '\n'.join(lines)

# Combine all batches 3-25
all_sql = []
for batch_num in range(3, 26):
    batch_file = f'scripts/articles/batch_{batch_num}_outlines.sql'
    if os.path.exists(batch_file):
        with open(batch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        cleaned = clean_sql_content(content)
        all_sql.append(f"-- Batch {batch_num}\n{cleaned}")
        print(f"Added batch {batch_num}")
    else:
        print(f"Warning: {batch_file} not found")

# Combine all SQL
combined_sql = '\n\n'.join(all_sql)

# Save combined SQL
output_file = 'scripts/articles/all_batches_combined.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("-- All outline updates from batches 3-25\n")
    f.write(f"-- Total: {len(all_sql)} batches, 230 UPDATE statements\n\n")
    f.write(combined_sql)

print(f"\nCombined SQL saved to: {output_file}")
print(f"Total batches: {len(all_sql)}")
print(f"Ready to execute via MCP Supabase execute_sql")

