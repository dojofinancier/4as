<!-- e6eeaa48-3ab8-4533-b265-ee4998914b45 769534d6-9ac3-429b-b534-6422d268b482 -->
# Course Blog System Implementation Plan

## Overview

Build a database-driven blog system that allows programmatic generation of course blog pages. Each page will display a full article about the course (study tips, curriculum overview, etc.) and link to the reservation page.

## Architecture

### Database Schema (Supabase)

Create a new `course_blog_posts` table:

- `id` (uuid, primary key)
- `course_slug` (text, unique, references courses.slug) - Course slug from courses table (for app compatibility)
- `blog_slug` (text, unique) - SEO-friendly slug for blog URL (e.g., "analyse-des-valeurs-mobilieres-1")
- `course_code` (text, references courses.code)
- `title` (text) - Blog post title
- `content` (text) - Full article content (markdown or HTML)
- `excerpt` (text) - Short description for previews
- `meta_description` (text) - SEO meta description
- `published` (boolean) - Whether post is live
- `published_at` (timestamp) - When post was published
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `author` (text, optional)
- `featured_image_url` (text, optional)

### Routing Structure

- Blog pages: `carredastutorat.com/[blog_slug]` (e.g., `carredastutorat.com/analyse-des-valeurs-mobilieres-1`)
  - Uses SEO-friendly `blog_slug` (generated from course title)
  - Falls back to `course_slug` if `blog_slug` not set (backward compatibility)
- Reservation link: `app.carredastutorat.com/cours/[course_slug]/reservation?code=[code]&source=blog`
  - Uses `course_slug` (from courses table) for app compatibility

## Implementation Steps

### Step 1: Database Setup

1. Create `course_blog_posts` table in Supabase with the schema above
2. Add foreign key relationship to `courses` table via `course_slug`
3. Add indexes on `course_slug`, `published`, and `published_at` for performance

### Step 2: TypeScript Types

**File**: `src/types.ts`

- Add `CourseBlogPost` interface matching the database schema
- Add helper types for blog post creation/updates

### Step 3: Supabase Functions

**File**: `src/lib/supabase.ts`

- Add `getBlogPostBySlug(slug: string)` - Fetch published blog post
- Add `getAllPublishedBlogPosts()` - For blog index/listing (optional)
- Add `createBlogPost(data)` - For AI generation workflow
- Add `updateBlogPost(slug, data)` - For content updates

### Step 4: Blog Post Component

**File**: `src/components/CourseBlogPost.tsx` (NEW)

- Display blog post content
- Render markdown/HTML content
- Show course information (title, code, institution)
- Include prominent CTA button linking to reservation page
- SEO meta tags (title, description)
- Responsive design matching current site style

### Step 5: Routing

**File**: `src/App.tsx`

- Add route: `<Route path="/:slug" element={<CourseBlogPost />} />`
- Ensure this route comes AFTER `/devenez-tuteur` routes to avoid conflicts
- Handle 404 for non-existent blog posts

### Step 6: Fetch Professor Ratings Script (Python)

**File**: `scripts/fetch-professor-ratings.py` (NEW)

**Purpose**: Populate `professor_ratings` table with data from RateMyProfessor API before generating blog content.

**Workflow**:
1. Connect to Supabase using service role key
2. Fetch all active courses from `courses` table
3. For each course:
   - Extract `institution` name (e.g., "ESG-UQAM", "McGill University")
   - Extract `domain` (department/subject area)
   - Use `ratemyprofessor.get_school_by_name(institution)` to get School object
   - Search for professors in that school using:
     - `ratemyprofessor.get_professor_by_school_and_name(school, professor_name)` 
     - Or search by department/domain keywords
   - For each professor found:
     - Extract rating data: `overall_rating`, `difficulty_rating`, `would_take_again`, `num_ratings`
     - Store in `professor_ratings` table with `course_slug` reference
     - Update `last_updated` timestamp
4. Handle errors gracefully (professor not found, school not found, etc.)
5. Log progress and results

**Inputs**:
- Supabase connection (URL + service role key from env vars)
- Course data from database (institution, domain, slug, code)

**Outputs**:
- Records inserted/updated in `professor_ratings` table
- Log file with results (courses processed, professors found, errors)

**Dependencies**:
- `RateMyProfessorAPI` Python package
- `supabase-py` Python package
- Environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`

**Note**: This script should be run BEFORE Step 7 (AI Content Generation) so professor data is available for blog post generation.

### Step 7: AI Content Generation Script

**File**: `scripts/generate-blog-posts.ts` (NEW)

**Prerequisites**: Step 6 (Professor Ratings) should be run first to populate professor data.

**Workflow**:
1. Fetch all active courses from Supabase
2. For each course:
   - Fetch course data (title, code, institution, domain, description_fr)
   - Fetch course customization fields (outline, website_description, prerequisites, required_in_programs)
   - Fetch professor ratings for this course (query `professor_ratings` table by `course_slug`)
   - Identify highest and lowest rated professors
   - Build AI prompt with all course data + professor insights
   - Call AI API to generate:
     - Full article content (min 900 words)
     - FAQ section
     - Meta description
     - H1 heading
   - Calculate word count
   - Generate JSON-LD structured data (Course, EducationalOrganization, BreadcrumbList, FAQPage)
   - Calculate similarity score (compare with existing posts)
   - Set `is_indexable = true` only if: word_count ≥ 900, similarity_score < threshold
   - Create/update blog post in database
   - Mark as published or draft based on QC checks

### Step 8: Content Rendering

- Install markdown renderer: `react-markdown` or `marked`
- Or use HTML if storing HTML directly
- Style content with Tailwind classes

### Step 9: SEO & Performance

- Add meta tags (title, description, Open Graph)
- Add structured data (JSON-LD) for course pages
- Implement caching strategy (optional: use React Query or SWR)
- Add loading states

## AI Generation Workflow

The script will:

1. Query Supabase for all active courses
2. For each course:
   - Fetch course data: title, code, institution, domain, description_fr
   - Fetch course customization data: outline, website_description, prerequisites, required_in_programs (if available)
   - Fetch professor ratings from `professor_ratings` table (highest and lowest rated)
   - Call AI API with enriched prompt including:
     - Course title, code, institution, domain
     - Course description and outline
     - Prerequisites and required programs
     - Professor ratings insights (e.g., "Students rate Professor X highest for this course")
     - Request: full article with study tips, curriculum overview, learning objectives, professor recommendations
3. Generate blog post content (min 900 words)
4. Calculate word count and similarity score
5. Generate FAQ content
6. Generate JSON-LD structured data
7. Insert/update in `course_blog_posts` table
8. Mark as published or draft based on QC checks (word count, similarity, etc.)

## Files to Create/Modify

**New Files:**

- `src/components/CourseBlogPost.tsx` - Blog post display component
- `src/components/BlogPostNotFound.tsx` - 404 for blog posts
- `scripts/generate-blog-posts.ts` - AI content generation script
- `scripts/fetch-professor-ratings.py` - Python script to fetch RateMyProfessor data
- `requirements.txt` - Python dependencies (RateMyProfessorAPI, supabase-py)
- `.env.example` - Add AI API key and Supabase service role key variables

**Modified Files:**

- `src/App.tsx` - Add blog post route
- `src/types.ts` - Add blog post types
- `src/lib/supabase.ts` - Add blog post functions
- `package.json` - Add dependencies (react-markdown, AI SDK if needed)

## Technical Decisions

1. **Content Format**: Store as markdown, render with `react-markdown` (flexible, easy to edit)
2. **Caching**: Use React Query or SWR for client-side caching
3. **AI Provider**: Use OpenAI API or similar (configurable via env var)
4. **Route Priority**: Blog routes come after specific routes (`/devenez-tuteur`) but before 404
5. **Reservation Link**: Use existing format with `source=blog` parameter

## Future Enhancements (Out of Scope)

- Admin UI for editing blog posts
- Blog index/listing page
- Related courses section
- Comments/engagement features