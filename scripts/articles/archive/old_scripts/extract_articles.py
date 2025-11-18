import json
import re

# Read the file
with open(r'c:\Users\User\.cursor\projects\c-Users-User-Desktop-4AS-HOME-code-workspace\agent-tools\f7cf3427-d7f2-4835-8571-175161bd4639.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# The content is escaped JSON, find the actual JSON array
# Look for the pattern: [{"articles": [...]}]
match = re.search(r'\[\{"articles":\s*(\[.*?\])\}\]', content, re.DOTALL)
if match:
    json_str = match.group(1)
    articles = json.loads(json_str)
    print(f"Found {len(articles)} articles")
    
    # Save
    with open('scripts/articles/all_remaining_articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to scripts/articles/all_remaining_articles.json")
    print(f"First article: {articles[0]['title']}")
else:
    print("Could not extract JSON")
    # Try alternative: decode the entire string first
    try:
        # The content might be double-encoded
        decoded = content.encode('utf-8').decode('unicode_escape')
        match2 = re.search(r'\[\{"articles":\s*(\[.*?\])\}\]', decoded, re.DOTALL)
        if match2:
            json_str = match2.group(1)
            articles = json.loads(json_str)
            print(f"Found {len(articles)} articles (alternative method)")
            with open('scripts/articles/all_remaining_articles.json', 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"Saved to scripts/articles/all_remaining_articles.json")
        else:
            print("Still could not extract")
    except Exception as e:
        print(f"Error: {e}")

