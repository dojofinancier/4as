#!/usr/bin/env python3
"""
Extract and prepare SQL batches for execution.
"""

import os
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file = os.path.join(script_dir, 'final_bulk_update_all.sql')

# Read the SQL file
with open(sql_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Split by batch markers
batches = re.split(r'-- Batch \d+', content)

# Remove the first empty element and header
batches = [b.strip() for b in batches[1:]]

print(f"Found {len(batches)} batches")

# Save each batch to a separate file
for i, batch in enumerate(batches, 1):
    batch_file = os.path.join(script_dir, f'batch_{i}_execute.sql')
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch.strip())
    print(f"Saved batch {i} to {batch_file}")

print("\nBatches are ready for execution via MCP Supabase!")

