# General Articles System Implementation Plan

## Overview

Create a new article generation system for general tutoring/studying/university topics (separate from course-specific blog posts). The system will use a two-step AI process (outline → full article), implement intelligent internal linking, add related articles, and include external resource links.

## Architecture

### Database Schema (Supabase)

Create a new `general_articles` table:

- `id` (uuid, primary key)
- `slug` (text, unique) - SEO-friendly URL slug
- `title` (text) - Article title (from CSV)
- `category` (text) - Category from CSV (e.g., "tutoring", "study-tips", "university-life")
- `tags` (text[]) - AI-generated tags array
- `keywords` (text[]) - AI-generated keywords array
- `draft_outline` (text) - AI-generated outline (stored for review)
- `content` (text) - Full article content (markdown)
- `excerpt` (text) - Short description for previews
- `meta_description` (text) - SEO meta description
- `h1` (text) - Main heading
- `internal_links` (jsonb) - Array of internal link objects: `[{slug: string, anchor_text: string, position: number}]`
- `related_articles` (uuid[]) - Array of 5 related article IDs
- `external_links` (jsonb) - Array of external link objects: `[{url: string, anchor_text: string, description: string, position: number}]`
- `word_count` (integer) - Article word count
- `similarity_score` (float) - Similarity with existing articles
- `is_indexable` (boolean) - SEO indexing flag
- `status` (text) - Status: 'draft_outline', 'draft', 'published'
- `published` (boolean) - Whether post is live
- `published_at` (timestamp) - When post was published
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `author` (text, optional)
- `featured_image_url` (text, optional)
- `json_ld` (jsonb) - Structured data for SEO

### Routing Structure

- Article pages: `carredastutorat.com/article/[slug]` (e.g., `carredastutorat.com/article/comment-reussir-ses-examens`)
- Separate from course blog routes to avoid conflicts

## Implementation Steps

### Step 1: Database Setup

1. Create `general_articles` table in Supabase with the schema above
2. Add indexes on:
   - `slug` (unique)
   - `category`
   - `status`
   - `published` and `published_at`
   - `tags` (GIN index for array searches)
   - `keywords` (GIN index for array searches)
3. Create a function to generate embeddings for semantic similarity (optional, for future enhancement)

### Step 2: TypeScript Types

**File**: `src/types.ts`

- Add `GeneralArticle` interface matching the database schema
- Add `GeneralArticleCreate` and `GeneralArticleUpdate` types
- Add helper types for internal/external links

### Step 3: Supabase Functions

**File**: `src/lib/supabase.ts`

- Add `getGeneralArticleBySlug(slug: string)` - Fetch published article
- Add `getAllPublishedGeneralArticles(limit, category?)` - For listings and related articles
- Add `getRelatedArticles(articleId, limit)` - Get related articles
- Add `createGeneralArticle(data)` - For AI generation workflow
- Add `updateGeneralArticle(slug, data)` - For content updates
- Add `getArticlesForLinking(category?, tags?, keywords?)` - For internal linking system

### Step 4: CSV Upload and Parsing Script

**File**: `scripts/articles/upload_article_titles.py` (NEW)

**Purpose**: Parse CSV with article titles/ideas and create initial database entries.

**CSV Format**:
```csv
title,category
Comment réussir ses examens,tutoring
Les meilleures techniques de mémorisation,study-tips
```

**Workflow**:
1. Read CSV file
2. For each row:
   - Generate slug from title
   - Create database entry with `status='draft_outline'`
   - Set `category` from CSV
   - Leave other fields empty for now
3. Log results and errors

### Step 5: Outline Generation Script

**File**: `scripts/articles/generate_outlines.py` (NEW)

**Purpose**: Generate article outlines using AI (first step).

**Workflow**:
1. Fetch all articles with `status='draft_outline'`
2. For each article:
   - Build AI prompt with title and category
   - Request outline for 1000-2000 word article
   - Store outline in `draft_outline` field
   - Update `status='draft'` (ready for full generation)
3. Process in batches of 5-10
4. Log progress and errors

**AI Prompt Structure**:
- Article title and category
- Request detailed outline with sections and subsections
- Target: 1000-2000 words
- French language
- Markdown format

### Step 6: Full Article Generation Script

**File**: `scripts/articles/generate_articles.py` (NEW)

**Purpose**: Generate full articles from outlines (second step).

**Workflow**:
1. Fetch all articles with `status='draft'` and `draft_outline` populated
2. For each article:
   - Build AI prompt with title, category, and outline
   - Request full article (1000-2000 words)
   - Generate tags and keywords
   - Calculate word count
   - Check similarity with existing articles
   - Store content, tags, keywords
   - Update `status='draft'` (ready for linking)
3. Process in batches of 5-10
4. Log progress and errors

**AI Prompt Structure**:
- Article title, category, and full outline
- Request complete article following outline
- Include tags and keywords generation
- French language, markdown format
- 1000-2000 words

### Step 7: Internal Linking Script

**File**: `scripts/articles/add_internal_links.py` (NEW)

**Purpose**: Add internal links between articles using AI semantic analysis.

**Workflow**:
1. Fetch all articles with `status='draft'` and content populated
2. For each article:
   - Fetch all other published articles (or articles ready for linking)
   - Use AI to analyze content and find relevant linking opportunities
   - AI suggests: anchor text, target article slug, position in text
   - Validate that target articles exist
   - Insert markdown links into content at suggested positions
   - Store link metadata in `internal_links` JSONB field
   - Update content with links inserted
3. Process in batches
4. Log progress and errors

**AI Prompt Structure**:
- Current article content
- List of available articles (title, slug, excerpt, tags, keywords)
- Request: identify 3-5 relevant linking opportunities with anchor text and position
- Ensure links are natural and contextual

### Step 8: Related Articles Script

**File**: `scripts/articles/add_related_articles.py` (NEW)

**Purpose**: Add 5 related articles at the end of each article.

**Workflow**:
1. Fetch all articles with content and internal links complete
2. For each article:
   - Fetch all other published articles
   - Use semantic similarity (tags, keywords, category) to find related articles
   - Select top 5 most relevant (excluding self)
   - Store IDs in `related_articles` array
   - Generate markdown section at end of article with related articles list
3. Process in batches
4. Log progress

**Matching Algorithm**:
- Priority: same category > shared tags > shared keywords
- Use word overlap for similarity scoring
- Ensure variety (not all from same category if possible)

### Step 9: External Links Script

**File**: `scripts/articles/add_external_links.py` (NEW)

**Purpose**: Add external links and resources using AI (with validation).

**Workflow**:
1. Fetch all articles ready for external links
2. For each article:
   - Build AI prompt with article content
   - Request relevant external links (academic sources, tools, resources)
   - AI must provide: URL, anchor text, description, position
   - Validate URLs (check if they exist, are accessible)
   - Filter out invalid/hallucinated links
   - Insert links into content at suggested positions
   - Add "Resources" section at end with all external links
   - Store link metadata in `external_links` JSONB field
3. Process in batches
4. Log progress and validation results

**AI Prompt Structure**:
- Article content
- Request: suggest 5-10 relevant external links (academic papers, tools, official resources)
- Must provide real, accessible URLs
- Include descriptions for each link

**URL Validation**:
- Check URL format
- Attempt HTTP HEAD request to verify accessibility
- Filter out broken/invalid links
- Log validation failures

### Step 10: Article Component

**File**: `src/components/GeneralArticle.tsx` (NEW)

- Display article content (markdown)
- Render internal links
- Display related articles section at bottom
- Display external resources section
- SEO meta tags
- Responsive design matching site style
- Similar structure to `CourseBlogPost.tsx`

### Step 11: Routing

**File**: `src/App.tsx`

- Add route: `<Route path="/article/:slug" element={<GeneralArticle />} />`
- Ensure route priority (after specific routes, before catch-all)
- Handle 404 for non-existent articles

### Step 12: Quality Control and Publishing

**File**: `scripts/articles/publish_articles.py` (NEW)

**Purpose**: Final QC and publishing workflow.

**Workflow**:
1. Fetch articles with all steps complete (`status='draft'`)
2. For each article:
   - Verify word count ≥ 1000
   - Verify grammar and natural sentence structure
   - Check similarity score (reject if too similar to existing)
   - Verify internal links are valid
   - Verify external links are accessible
   - Verify related articles exist
   - Generate meta description if missing
   - Generate JSON-LD structured data
   - Set `published=true`, `status='published'`, `published_at=now()`
   - Set `is_indexable=true` if passes all checks
3. Log results

## Files to Create/Modify

**New Files:**
- `scripts/articles/upload_article_titles.py` - CSV upload script
- `scripts/articles/generate_outlines.py` - Outline generation
- `scripts/articles/generate_articles.py` - Full article generation
- `scripts/articles/add_internal_links.py` - Internal linking
- `scripts/articles/add_related_articles.py` - Related articles
- `scripts/articles/add_external_links.py` - External links with validation
- `scripts/articles/publish_articles.py` - Final QC and publishing
- `scripts/articles/README.md` - Documentation
- `src/components/GeneralArticle.tsx` - Article display component
- `src/components/ArticleNotFound.tsx` - 404 component

**Modified Files:**
- `src/App.tsx` - Add article route
- `src/types.ts` - Add general article types
- `src/lib/supabase.ts` - Add general article functions

## Technical Decisions

1. **Content Format**: Markdown (same as course blogs) for consistency
2. **Language**: French (same as course blogs)
3. **AI Provider**: OpenAI API (same as course blogs, configurable)
4. **Batch Processing**: 5-10 articles per batch (similar to course blogs)
4. **Similarity Checking**: Reuse logic from course blog system
5. **Status Workflow**: `draft_outline` → `draft` → `published`
6. **Link Storage**: JSONB for flexibility and querying
7. **URL Validation**: Use `requests` library for HTTP validation

## Workflow Summary

1. Upload CSV → Create database entries (`status='draft_outline'`)
2. Generate outlines → Store in `draft_outline` (`status='draft'`)
3. Generate full articles → Store content, tags, keywords (`status='draft'`)
4. Add internal links → Update content with links (`status='draft'`)
5. Add related articles → Update `related_articles` array (`status='draft'`)
6. Add external links → Update content with validated links (`status='draft'`)
7. Publish → QC check and set `published=true` (`status='published'`)

## Future Enhancements (Out of Scope)

- Admin UI for reviewing outlines before generation
- Manual override for internal/external links
- Article categories/tags filtering page
- Search functionality
- Analytics tracking

