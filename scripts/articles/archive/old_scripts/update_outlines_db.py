#!/usr/bin/env python3
"""Extract clean outlines from SQL and update database via MCP."""

import re

# Read the SQL file
with open('scripts/articles/batch_1_outlines.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract UPDATE statements
updates = re.findall(r"UPDATE general_articles SET draft_outline = '(.*?)', status = 'draft'", content, re.DOTALL)

# Clean each outline (remove markdown code blocks)
cleaned_updates = []
for update in updates:
    # Remove ```markdown at start and ``` at end
    cleaned = re.sub(r'^```markdown\n', '', update)
    cleaned = re.sub(r'\n```$', '', cleaned)
    cleaned_updates.append(cleaned)

# Get slugs
slugs = re.findall(r"WHERE slug = '([^']+)';", content)

# Generate clean SQL
sql_statements = []
for i, (slug, outline) in enumerate(zip(slugs, cleaned_updates)):
    # Escape single quotes for SQL
    outline_escaped = outline.replace("'", "''")
    sql = f"UPDATE general_articles SET draft_outline = '{outline_escaped}', status = 'draft', updated_at = NOW() WHERE slug = '{slug}';"
    sql_statements.append(sql)

# Save clean SQL
with open('scripts/articles/batch_1_outlines_final.sql', 'w', encoding='utf-8') as f:
    f.write("-- Clean outline updates\n\n")
    for sql in sql_statements:
        f.write(sql + "\n\n")

print(f"Generated {len(sql_statements)} clean SQL statements")

