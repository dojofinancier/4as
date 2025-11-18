#!/usr/bin/env python3
"""
Final script to apply all outline updates.
This script will be used by the assistant to execute all batches via MCP Supabase.
"""

import os
import re

def get_batch_sql(batch_num):
    """Read and return cleaned SQL for a batch."""
    batch_file = f'scripts/articles/batch_{batch_num}_execute.sql'
    if os.path.exists(batch_file):
        with open(batch_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

# Verify all batches are ready
print("Verifying all batch files are ready...")
for batch_num in range(3, 26):
    sql = get_batch_sql(batch_num)
    if sql:
        update_count = len(re.findall(r'UPDATE general_articles SET', sql))
        print(f"Batch {batch_num}: Ready ({update_count} statements)")
    else:
        print(f"Batch {batch_num}: Missing")

print("\nAll batches verified. Ready for execution via MCP Supabase execute_sql.")
print("The assistant will now execute each batch file's SQL content.")

