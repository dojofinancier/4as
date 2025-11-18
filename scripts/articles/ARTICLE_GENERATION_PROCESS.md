# Article Generation Process

## Overview

This document explains the process for generating full article content from outlines using the improved prompts from `article_prompts.md`.

## Process Flow

### Step 1: Fetch Articles Ready for Generation

**Query:** Fetch all articles from `general_articles` table where:
- `status = 'draft'` (outline has been generated)
- `draft_outline IS NOT NULL` (outline exists)
- `content IS NULL` (no content generated yet)

**Implementation:**
```python
articles = supabase.from_('general_articles')\
    .select('id, slug, title, category, draft_outline')\
    .eq('status', 'draft')\
    .not_('draft_outline', 'is', 'null')\
    .is_('content', 'null')\
    .execute()
```

### Step 2: Process Articles in Batches

**Batch Size:** 5-10 articles per batch
- **Reason:** Balance between API efficiency and error recovery
- **Rate Limiting:** 2-3 second delay between API calls (longer than outlines due to larger content)
- **Error Handling:** If one article fails, continue with the rest in the batch

### Step 3: Generate Article Using Two-Step Process

#### Step 3a: Initial Article Generation

**Prompt Used:** Third prompt from `article_prompts.md` (lines 257-396)
- **Model:** `gpt-5-nano` (same as outlines for cost efficiency)
- **Input Variables:**
  - `{{ARTICLE_TITLE}}` → Article title from database
  - `{{OUTLINE_HERE}}` → The `draft_outline` from database

**Prompt Structure:**
1. System role: Expert content strategist and tutor
2. Audience context: Quebec business students (18-25)
3. Requirements:
   - 1,500-2,000 words
   - Follow outline structure (H2/H3 hierarchy)
   - Use "tu" form (tutoiement)
   - Direct, conversational tone
   - Fact-heavy and research-driven
   - Concrete examples
4. Style guidelines: Personal, supportive, practical

**API Call:**
```python
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_with_title_and_outline}
    ],
    max_completion_tokens=4000,  # Larger than outlines (full articles)
    reasoning_effort="minimal",
    verbosity="high"  # High verbosity for detailed blog content
    # Note: gpt-5-nano doesn't support custom temperature, uses default (1)
)
```

#### Step 3b: Improve Article (Optional but Recommended)

**Prompt Used:** Fourth prompt from `article_prompts.md` (lines 397-535)
- **Model:** Same as Step 3a
- **Input:** The article generated in Step 3a
- **Purpose:** Refine and improve article quality

**Process:**
1. Analyze the initial article for:
   - Generic/vague sections
   - Missing practical elements
   - Weak explanations
   - Missing examples
   - Tone inconsistencies
2. Rewrite the entire article with improvements
3. Ensure all requirements are met (word count, structure, tone, etc.)

**Decision Point:** 
- **Option A:** Always improve (higher quality, more cost)
- **Option B:** Only improve if initial article quality is low (cost-efficient)
- **Option C:** Skip improvement step (fastest, lower quality)

**Recommendation:** Option A for first batch, then evaluate quality to decide.

### Step 4: Extract Metadata

After generation, extract:
- **H1:** First heading in content (or use title as fallback)
- **Meta Description:** First 150 characters of content (cleaned)
- **Excerpt:** First 200 characters of content (cleaned)
- **Word Count:** Count words in article (excluding markdown)
- **Tags:** Extract from response (if provided) or generate
- **Keywords:** Extract from response (if provided) or generate

### Step 5: Validate Article Quality

Before saving, validate:
- ✅ Word count: 1,500-2,000 words (approximate)
- ✅ Has H1 heading
- ✅ Follows outline structure (H2/H3 sections match)
- ✅ Is in French
- ✅ No markdown formatting issues
- ✅ Tags and keywords extracted

### Step 6: Update Database

**Update Query:**
```python
update_data = {
    'content': article_text,
    'h1': h1,
    'meta_description': meta_desc,
    'excerpt': excerpt,
    'tags': tags_array,
    'keywords': keywords_array,
    'word_count': word_count,
    'status': 'content_generated',  # Move to next stage
    'updated_at': datetime.now(timezone.utc).isoformat()
}

result = supabase.from_('general_articles')\
    .update(update_data)\
    .eq('slug', article_slug)\
    .execute()
```

**Error Handling:**
- If update fails due to slug mismatch, use fuzzy matching
- Log all failures for later review
- Continue processing remaining articles

### Step 7: Logging and Monitoring

**Log Each Article:**
- Article title and slug
- Generation success/failure
- Word count
- Tags/keywords count
- Processing time
- Any errors or warnings

**Log File:** `scripts/articles/article_generation.log`

**Progress Tracking:**
- Total articles to process
- Articles completed
- Articles failed
- Estimated time remaining
- Average word count
- Average processing time per article

## Implementation Script Structure

```python
#!/usr/bin/env python3
"""
Generate full articles from outlines using improved prompts.
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

# 1. Load environment variables
load_dotenv()

# 2. Initialize clients
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Load prompts from article_prompts.md
ARTICLE_PROMPT = load_prompt('article_prompts.md', 'PROMPT TO DRAFT THE ARTICLE')
IMPROVE_PROMPT = load_prompt('article_prompts.md', 'PROMPT TO IMPROVE THE DRAFT ARTICLE')

# 4. Fetch articles
articles = fetch_articles_ready_for_generation()

# 5. Process in batches
for batch in chunk(articles, batch_size=5):
    for article in batch:
        try:
            # Generate initial article
            article_content = generate_article(article, ARTICLE_PROMPT)
            
            # Improve article
            improved_article = improve_article(article_content, IMPROVE_PROMPT)
            
            # Extract metadata
            metadata = extract_metadata(improved_article)
            
            # Validate
            if validate_article(improved_article, metadata):
                # Update database
                update_article_content(article['slug'], improved_article, metadata)
                log_success(article)
            else:
                log_validation_error(article)
        except Exception as e:
            log_error(article, e)
    
    # Delay between batches
    time.sleep(2)
```

## Running in Background with Terminal Tracking

### Option 1: Run with nohup (Linux/Mac)
```bash
nohup python scripts/articles/generate_articles_v2.py > article_gen_output.log 2>&1 &
tail -f article_gen_output.log
```

### Option 2: Run in Background Process (Windows PowerShell)
```powershell
Start-Process python -ArgumentList "scripts\articles\generate_articles_v2.py" -NoNewWindow -RedirectStandardOutput article_gen_output.log -RedirectStandardError article_gen_error.log
Get-Content article_gen_output.log -Wait -Tail 50
```

### Option 3: Use Python's logging (Recommended)
The script will:
- Log to both file (`article_generation.log`) and console
- Show real-time progress in terminal
- Continue running even if terminal is closed (if using nohup/background)

**To monitor progress:**
```bash
# In one terminal, run the script
python scripts/articles/generate_articles_v2.py

# In another terminal, watch the log file
tail -f scripts/articles/article_generation.log
```

## Quality Assurance

### Before Starting Batch:
1. Test with 1-2 sample articles
2. Review generated articles for quality
3. Check word count, structure, tone
4. Adjust prompts if needed
5. Verify database updates work correctly

### During Processing:
1. Monitor log file for errors
2. Check article quality periodically (every 10 articles)
3. Pause if error rate > 10%
4. Review failed articles manually
5. Monitor word counts (should be 1,500-2,000)

### After Completion:
1. Generate summary report:
   - Total processed
   - Success rate
   - Average word count
   - Average processing time
   - Common errors
2. Review sample articles for quality
3. Fix any failed articles manually or re-run

## Cost Estimation

**Assumptions:**
- Average article: ~2,500 tokens (input) + ~3,000 tokens (output) = ~5,500 tokens
- Improvement step: ~3,500 tokens (input) + ~3,000 tokens (output) = ~6,500 tokens
- Model: gpt-5-nano (cost-efficient)
- Cost per 1K tokens: ~$0.0001-0.0002

**Per Article:**
- Initial generation: ~$0.0006-0.0011
- Improvement: ~$0.0007-0.0013
- **Total: ~$0.0013-0.0024 per article**

**For 100 Articles:**
- **Estimated cost: $0.13-0.24** (very affordable!)

## Error Recovery

### Common Issues:

1. **Slug Mismatch**
   - Use fuzzy string matching
   - Log original vs. matched slug
   - Manual review if needed

2. **API Rate Limits**
   - Implement exponential backoff
   - Reduce batch size
   - Add longer delays (2-3 seconds)

3. **Invalid Article Structure**
   - Log the article for review
   - Retry with adjusted prompt
   - Manual fix if retry fails

4. **Word Count Issues**
   - If too short: Request regeneration with emphasis on length
   - If too long: Accept it (better than too short)
   - Log for review

5. **Database Connection Issues**
   - Retry with exponential backoff
   - Save articles to local file as backup
   - Resume from last successful article

## Next Steps After Article Generation

Once all articles are generated:
1. Review sample articles for quality
2. Run quality control checks (grammar, etc.)
3. Add internal/external links
4. Add related articles
5. Publish articles

## Notes

- **Model Selection:** Using gpt-5-nano for cost efficiency
- **Model Parameters:** 
  - No `temperature` parameter (uses default 1)
  - Use `max_completion_tokens` instead of `max_tokens`
  - `reasoning_effort`: "minimal"
  - `verbosity`: "high" (for detailed blog content)
- **Prompt Versioning:** Track which prompt version was used for each article
- **Checkpointing:** Save progress every 10 articles to enable resumption
- **Geographical References:** Avoid explicit mentions like "(les étudiants du Québec)" - context is assumed

