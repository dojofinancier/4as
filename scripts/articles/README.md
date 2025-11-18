# General Articles Generation Scripts

This directory contains scripts for generating, managing, and publishing general tutoring/studying/university-related articles.

## Directory Structure

```
scripts/articles/
├── README.md                       # This file
├── articles_250_real_titles.csv    # Input CSV with article titles and categories
│
├── Core Scripts (Active)
├── generate_outlines.py            # Step 1: Generate AI outlines for articles
├── auto_update_outlines.py         # Update articles with generated outlines
├── fix_failed_outlines.py          # Fix articles with slug mismatches
├── generate_articles.py            # Step 2: Generate full article content
├── quality_control_grammar.py      # Step 2.5: Quality control - grammar check
├── add_internal_links.py           # Step 3: Add internal links to articles
├── add_related_articles.py         # Step 4: Add related articles
├── add_external_links.py           # Step 5: Add external resources
├── publish_articles.py             # Step 6: Publish articles to production
│
└── archive/                        # Historical files (not actively used)
    ├── batch_sql/                  # Old batch SQL files
    ├── batch_updates/              # Individual update SQL files
    ├── old_scripts/                # Deprecated Python scripts
    ├── logs/                       # Historical log files
    └── seq_updates/                # Old sequential update attempts
```

## Workflow

The article generation process follows these steps:

### 1. Generate Outlines (Step 1)
```bash
python scripts/articles/generate_outlines.py
```
- Fetches articles with `status='draft_outline'`
- Generates detailed outlines using OpenAI API (gpt-5-nano)
- Updates articles with `draft_outline` and sets `status='draft'`
- Processes in batches for efficiency

### 2. Fix Any Failed Updates
```bash
python scripts/articles/fix_failed_outlines.py
```
- Identifies articles that failed to update (slug mismatches)
- Uses fuzzy string matching (Levenshtein distance) to find correct slugs
- Retries updates with corrected slugs

### 3. Generate Full Articles (Step 2)
```bash
python scripts/articles/generate_articles.py
```
- Fetches articles with `status='draft'`
- Generates full article content (1000-2000 words) based on outline
- Generates tags, keywords, meta descriptions, H1, excerpt
- Updates articles with content and sets `status='content_generated'`

### 3.5. Quality Control: Grammar Check (Step 2.5)
```bash
python scripts/articles/quality_control_grammar.py
```
- **Run after article generation, before publishing**
- Checks and corrects grammatical errors in titles, H1, meta descriptions, and excerpts
- Fixes common issues like "en la/le" → "en", "de le" → "du", etc.
- Uses AI (gpt-5-nano) to ensure correct French grammar
- Updates articles directly in the database
- Processes in batches of 20 articles

**Common corrections:**
- "Optimiser sa réussite en la lecture" → "Optimiser sa réussite en lecture"
- "Secrets pour réussir en le marketing" → "Secrets pour réussir en marketing"
- "Approche pratique de le sommeil" → "Approche pratique du sommeil"

### 4. Add Internal Links (Step 3)
```bash
python scripts/articles/add_internal_links.py
```
- Analyzes article content and existing articles
- Identifies relevant internal linking opportunities
- Inserts contextual internal links
- Updates `internal_links` field

### 5. Add Related Articles (Step 4)
```bash
python scripts/articles/add_related_articles.py
```
- Finds 5 related articles based on category, tags, and keywords
- Updates `related_articles` field with article IDs

### 6. Add External Links (Step 5)
```bash
python scripts/articles/add_external_links.py
```
- Generates relevant external resource links
- Validates URLs for accessibility
- Updates `external_links` field

### 7. Publish Articles (Step 6)
```bash
python scripts/articles/publish_articles.py
```
- Reviews articles ready for publication
- Sets `published=true`, `status='published'`
- Updates `published_at` timestamp

## Database Schema

Articles are stored in the `general_articles` table with the following key fields:

- `id` (uuid): Unique identifier
- `slug` (text): SEO-friendly URL slug
- `title` (text): Article title
- `category` (text): Article category
- `tags` (text[]): AI-generated tags
- `keywords` (text[]): SEO keywords
- `draft_outline` (text): AI-generated outline
- `content` (text): Full article content (Markdown)
- `excerpt` (text): Short preview
- `meta_description` (text): SEO meta description
- `h1` (text): Main heading
- `internal_links` (jsonb): Internal link objects
- `related_articles` (uuid[]): Related article IDs
- `external_links` (jsonb): External resource links
- `word_count` (integer): Article word count
- `status` (text): 'draft_outline' | 'draft' | 'content_generated' | 'links_added' | 'published'
- `published` (boolean): Publication status
- `is_indexable` (boolean): SEO indexing flag

## Environment Variables

Required in `.env`:
```
OPENAI_API_KEY=sk-...
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## Key Learnings & Best Practices

Based on our experience generating 250+ article outlines:

1. **Use Direct SDK Calls**: The Supabase Python SDK is more reliable than SQL files for large batches
2. **Implement Checkpointing**: Save progress regularly to enable resumption after interruptions
3. **Fuzzy Matching for Slugs**: Handle encoding differences (apostrophes, accents) with Levenshtein distance
4. **Batch Processing**: Process 5-10 articles at a time for OpenAI API efficiency
5. **Comprehensive Logging**: Log all successes, failures, and warnings for debugging
6. **Error Recovery**: Implement retry logic with exponential backoff for API calls
7. **Status Tracking**: Use clear status fields to track progress through the pipeline

## Archive Directory

The `archive/` directory contains historical files from earlier implementation attempts:
- 665+ SQL files from batch processing attempts
- Multiple iteration scripts that were superseded
- These files are preserved for reference but not actively used

## Notes

- All article content is generated in **French**
- Content is in **Markdown** format for consistent rendering
- Articles target 1000-2000 words for SEO optimization
- AI uses `gpt-5-nano` for cost efficiency (~$0.19 for 225 articles - 33% cheaper than gpt-4o-mini)
