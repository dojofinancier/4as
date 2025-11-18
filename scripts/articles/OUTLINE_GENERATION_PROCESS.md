# Outline Generation Process

## Overview

This document explains the precise process for generating article outlines using the improved prompts from `article_prompts.md` and updating the database systematically.

## Process Flow

### Step 1: Fetch Articles Needing Outlines

**Query:** Fetch all articles from `general_articles` table where:
- `status = 'draft_outline'`
- `draft_outline IS NULL` (no outline exists yet)

**Implementation:**
```python
articles = supabase.from_('general_articles')\
    .select('id, slug, title, category')\
    .eq('status', 'draft_outline')\
    .is_('draft_outline', 'null')\
    .execute()
```

### Step 2: Process Articles in Batches

**Batch Size:** 5-10 articles per batch
- **Reason:** Balance between API efficiency and error recovery
- **Rate Limiting:** 0.5-1 second delay between API calls
- **Error Handling:** If one article fails, continue with the rest in the batch

### Step 3: Generate Outline Using Two-Step Process

#### Step 3a: Initial Outline Generation

**Prompt Used:** First prompt from `article_prompts.md` (lines 1-135)
- **Model:** Latest AI model (as specified by user - likely `gpt-4o` or `gpt-4-turbo`)
- **Input Variables:**
  - `{{ARTICLE_TITLE}}` → Article title from database
  - `{{ARTICLE_GOAL}}` → Generated from title/category (optional, can be inferred)

**Prompt Structure:**
1. System role: Expert content strategist and tutor
2. Audience context: Quebec business students (18-25)
3. Requirements:
   - 8-12 H2 sections
   - 2-4 H3 subsections per H2
   - Each H3 has explanatory sentence in parentheses
   - Must include: "Erreurs fréquentes", "Astuces de tuteur", "Mini-checklist"
4. Content quality rules: Specific, practical, research-driven
5. Style guidelines: Direct, conversational, fact-heavy

**API Call:**
```python
response = client.chat.completions.create(
    model="gpt-5-nano",  # Using gpt-5-nano for cost efficiency
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_with_title}
    ],
    max_completion_tokens=2000,  # gpt-5-nano uses max_completion_tokens instead of max_tokens
    reasoning_effort="minimal",  # Prioritize content generation over reasoning
    verbosity="medium"  # Medium verbosity for structured outlines
    # Note: gpt-5-nano doesn't support custom temperature, uses default (1)
)
```

#### Step 3b: Improve Outline (Optional but Recommended)

**Prompt Used:** Second prompt from `article_prompts.md` (lines 136-256)
- **Model:** Same as Step 3a
- **Input:** The outline generated in Step 3a
- **Purpose:** Refine and improve the outline quality

**Process:**
1. Analyze the initial outline for:
   - Generic/vague sections
   - Missing practical elements
   - Weak headlines
   - Missing research opportunities
2. Rewrite the entire outline with improvements
3. Ensure all requirements are met (H2/H3 structure, explanatory sentences, etc.)

**API Call for Improvement:**
```python
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "system", "content": improve_system_prompt},
        {"role": "user", "content": improve_prompt_with_outline}
    ],
    max_completion_tokens=2000,  # Same as initial generation
    reasoning_effort="minimal",
    verbosity="medium"
    # Note: gpt-5-nano doesn't support custom temperature, uses default (1)
)
```

**Decision Point:** 
- **Option A:** Always improve (higher quality, more cost)
- **Option B:** Only improve if initial outline quality is low (cost-efficient)
- **Option C:** Skip improvement step (fastest, lower quality)

**Recommendation:** Option A for first batch, then evaluate quality to decide.

### Step 4: Validate Outline Structure

Before saving, validate that the outline:
- ✅ Has exactly 1 H1 (the title)
- ✅ Has 8-12 H2 sections
- ✅ Each H2 has 2-4 H3 subsections
- ✅ Each H3 has explanatory sentence in parentheses
- ✅ Includes required sections: "Erreurs fréquentes des étudiants", "Astuces de tuteur (pro tips)", "Mini-checklist à appliquer immédiatement"
- ✅ Is in French
- ✅ No markdown formatting issues

### Step 5: Update Database

**Update Query:**
```python
update_data = {
    'draft_outline': outline_text,
    'status': 'draft',  # Move to next stage
    'updated_at': datetime.utcnow().isoformat()
}

result = supabase.from_('general_articles')\
    .update(update_data)\
    .eq('slug', article_slug)\
    .execute()
```

**Error Handling:**
- If update fails due to slug mismatch, use fuzzy matching (Levenshtein distance)
- Log all failures for later review
- Continue processing remaining articles

### Step 6: Logging and Monitoring

**Log Each Article:**
- Article title and slug
- Generation success/failure
- Outline length (word count)
- Processing time
- Any errors or warnings

**Log File:** `scripts/articles/outline_generation.log`

**Progress Tracking:**
- Total articles to process
- Articles completed
- Articles failed
- Estimated time remaining

## Implementation Script Structure

```python
#!/usr/bin/env python3
"""
Generate outlines for articles using improved prompts.
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
OUTLINE_PROMPT = load_prompt('article_prompts.md', 'PROMPT TO GENERATE OUTLINE')
IMPROVE_PROMPT = load_prompt('article_prompts.md', 'PROMPT TO IMPROVE OUTLINE')

# 4. Fetch articles
articles = fetch_articles_needing_outlines()

# 5. Process in batches
for batch in chunk(articles, batch_size=5):
    for article in batch:
        try:
            # Generate initial outline
            outline = generate_outline(article, OUTLINE_PROMPT)
            
            # Improve outline
            improved_outline = improve_outline(outline, IMPROVE_PROMPT)
            
            # Validate
            if validate_outline(improved_outline):
                # Update database
                update_article_outline(article['slug'], improved_outline)
                log_success(article)
            else:
                log_validation_error(article)
        except Exception as e:
            log_error(article, e)
    
    # Delay between batches
    time.sleep(1)
```

## Quality Assurance

### Before Starting Batch:
1. Test with 1-2 sample articles
2. Review generated outlines for quality
3. Adjust prompts if needed
4. Verify database updates work correctly

### During Processing:
1. Monitor log file for errors
2. Check outline quality periodically (every 10 articles)
3. Pause if error rate > 10%
4. Review failed articles manually

### After Completion:
1. Generate summary report:
   - Total processed
   - Success rate
   - Average outline length
   - Common errors
2. Review sample outlines for quality
3. Fix any failed articles manually or re-run

## Cost Estimation

**Assumptions:**
- Average outline: ~1500 tokens (input + output)
- Improvement step: ~2000 tokens (input + output)
- Model: gpt-5-nano (cost-efficient)
- Cost per 1K tokens: ~$0.0001-0.0002 (gpt-5-nano is very cost-efficient)

**Per Article:**
- Initial generation: ~$0.0002-0.0003
- Improvement: ~$0.0002-0.0004
- **Total: ~$0.0004-0.0007 per article**

**For 100 Articles:**
- **Estimated cost: $0.04-0.07** (very affordable!)

**Note:** gpt-5-nano is significantly cheaper than gpt-4o (~33% cheaper than gpt-4o-mini according to README)

## Error Recovery

### Common Issues:

1. **Slug Mismatch**
   - Use fuzzy string matching
   - Log original vs. matched slug
   - Manual review if needed

2. **API Rate Limits**
   - Implement exponential backoff
   - Reduce batch size
   - Add longer delays

3. **Invalid Outline Structure**
   - Log the outline for review
   - Retry with adjusted prompt
   - Manual fix if retry fails

4. **Database Connection Issues**
   - Retry with exponential backoff
   - Save outlines to local file as backup
   - Resume from last successful article

## Next Steps After Outline Generation

Once all outlines are generated:
1. Review sample outlines for quality
2. Run `generate_articles.py` to create full content
3. Run quality control checks
4. Add internal/external links
5. Publish articles

## Notes

- **Model Selection:** Using gpt-5-nano for cost efficiency (~33% cheaper than gpt-4o-mini)
- **Model Parameters:** 
  - No `temperature` parameter (uses default 1)
  - Use `max_completion_tokens` instead of `max_tokens`
  - `reasoning_effort`: "minimal" (prioritize content generation)
  - `verbosity`: "low" | "medium" | "high" (use "medium" for outlines)
- **Prompt Versioning:** Track which prompt version was used for each article
- **Checkpointing:** Save progress every 10 articles to enable resumption
- **Parallel Processing:** Can be parallelized but watch API rate limits

