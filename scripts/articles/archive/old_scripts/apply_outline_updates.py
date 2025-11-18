#!/usr/bin/env python3
"""Apply outline updates from SQL file to database via MCP."""

import re

# Read SQL file
with open('scripts/articles/batch_1_outlines_final.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Extract individual UPDATE statements
# Split by UPDATE statements
updates = re.split(r'(UPDATE general_articles SET)', sql_content)
updates = [updates[i] + updates[i+1] for i in range(1, len(updates), 2)]

print(f"Found {len(updates)} UPDATE statements")
print("\nSQL statements ready to execute via MCP Supabase")
print("The assistant will execute these statements individually")

# Save individual statements for reference
for i, update in enumerate(updates, 1):
    with open(f'scripts/articles/update_{i}.sql', 'w', encoding='utf-8') as f:
        f.write(update.strip())
    print(f"Saved update_{i}.sql")

