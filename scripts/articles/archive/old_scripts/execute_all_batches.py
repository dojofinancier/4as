#!/usr/bin/env python3
"""
Execute all SQL batches via MCP Supabase.
This script reads each batch file and outputs instructions for execution.
"""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))

batches = [1, 2, 3, 4]

for batch_num in batches:
    batch_file = os.path.join(script_dir, f'batch_{batch_num}_execute.sql')
    
    if not os.path.exists(batch_file):
        print(f"Batch {batch_num} file not found: {batch_file}")
        continue
    
    with open(batch_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"\n{'='*60}")
    print(f"Batch {batch_num}")
    print(f"SQL Length: {len(sql_content)} characters")
    print(f"File: {batch_file}")
    print(f"{'='*60}")
    print("\nSQL is ready for execution via MCP Supabase")
    print("The assistant will execute this batch using mcp_supabase_execute_sql")

print("\n\nAll batches are ready for execution!")
print("The assistant will now execute each batch sequentially via MCP Supabase.")
