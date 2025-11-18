# Course-Specific Blog Posts Generation Scripts

This directory contains scripts for generating course-specific blog posts (e.g., FIN3500, MATH101, etc.).

## Directory Structure

```
scripts/blog/
├── README.md                      # This file
├── generate-blog-posts.py         # Main script for course blog generation
├── test_fin3500_generation.py     # Test script for validating generation
│
└── archive/                       # Historical files (not actively used)
    ├── batch_results/             # Old batch result JSON files
    ├── logs/                      # Historical log files
    ├── old_scripts/               # Deprecated Python scripts
    └── sql_files/                 # Old SQL update files
```

## Purpose

This directory is specifically for **course-specific blog posts** that are tied to individual courses in the database (e.g., "Study Tips for FIN3500", "How to Ace MATH101").

For **general articles** (tutoring, studying, university topics not tied to specific courses), see `scripts/articles/` instead.

## Main Script

### `generate-blog-posts.py`

Generates blog posts for specific courses using AI.

**Usage:**
```bash
python scripts/blog/generate-blog-posts.py --course FIN3500
```

**Features:**
- Fetches course information from the `courses` table
- Generates SEO-optimized blog post content
- Creates title, slug, content, meta tags, and JSON-LD
- Saves posts to the `course_blogs` table
- Uses OpenAI API (gpt-5-nano) for content generation

## Database Schema

Course blogs are stored in the `course_blogs` table:
- `id` (uuid): Unique identifier
- `course_id` (uuid): Reference to course in `courses` table
- `slug` (text): SEO-friendly URL slug
- `title` (text): Blog post title
- `content` (text): Full blog post content (Markdown)
- `meta_description` (text): SEO meta description
- `h1` (text): Main heading
- `word_count` (integer): Content word count
- `is_indexable` (boolean): SEO indexing flag
- `published` (boolean): Publication status
- `json_ld` (jsonb): Structured data for SEO
- `created_at`, `updated_at`: Timestamps

## Workflow

1. **Identify Course**: Select a course from the database that needs a blog post
2. **Generate Content**: Run `generate-blog-posts.py` with the course code
3. **Review**: Check generated content for quality and accuracy
4. **Publish**: Update `published` flag to make post live

## Environment Variables

Required in `.env`:
```
OPENAI_API_KEY=sk-...
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## Testing

Use `test_fin3500_generation.py` to test the generation process:
```bash
python scripts/blog/test_fin3500_generation.py
```

## Key Differences from General Articles

| Feature | Course Blogs (this dir) | General Articles (`scripts/articles/`) |
|---------|------------------------|----------------------------------------|
| **Scope** | Specific courses | General topics |
| **Database Table** | `course_blogs` | `general_articles` |
| **Input** | Course data from DB | CSV with titles |
| **Linking** | Linked to course pages | Standalone articles |
| **Volume** | One per course (~500) | High volume (250+) |
| **Process** | Single-step generation | Multi-step pipeline (outline → content → links) |

## Notes

- Course blogs are typically one post per course
- Content is generated in **French**
- Uses **Markdown** format
- SEO-optimized with meta tags and JSON-LD structured data
