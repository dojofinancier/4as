# Scripts

This directory contains utility scripts for the project, organized by purpose.

## Directory Structure

```
scripts/
├── articles/          # General articles generation system
├── blog/              # Course blog posts generation system
├── utils/             # Shared utilities (ranking, etc.)
└── [root scripts]     # General utilities
```

---

## General Articles Generation System

See [articles/README.md](articles/README.md) for complete documentation.

**Purpose:** Generate high-volume general tutoring/studying/university articles (250+ articles).

**Key Scripts:**
- `generate_outlines.py` - Generate AI-powered outlines
- `auto_update_outlines.py` - Apply outlines to database
- `fix_failed_outlines.py` - Fix slug mismatches
- `generate_articles.py` - Generate full article content
- `add_internal_links.py` - Add contextual internal links
- `add_related_articles.py` - Add related article suggestions
- `add_external_links.py` - Add external resources
- `publish_articles.py` - Publish to production

**Workflow:**
1. **CSV Input** → Article titles and categories loaded into database
2. **Generate Outlines** → AI creates detailed 1000-2000 word outlines
3. **Generate Articles** → AI writes full articles based on outlines
4. **Add Internal Links** → AI adds contextual links to related articles
5. **Add Related Articles** → System finds 5 related articles per post
6. **Add External Links** → AI suggests validated external resources
7. **Publish** → Quality control and publishing

---

## Course Blog Posts Generation System

See [blog/README.md](blog/README.md) for complete documentation.

**Purpose:** Generate course-specific blog posts tied to individual courses (e.g., "Study Tips for FIN3500").

**Key Script:** `generate-blog-posts.py`

**Features:**
- Course overview and difficulty assessment
- Study strategies by domain
- Professor rankings integration
- Tutoring benefits and CTAs
- SEO optimization with JSON-LD structured data

**Workflow:**
1. Fetch course data from database
2. Generate blog content using AI (gpt-4o-mini)
3. Create SEO meta tags and structured data
4. Save to `course_blogs` table

**Usage:**
```bash
python scripts/blog/generate-blog-posts.py --course FIN3500
```

---

## Professor Ranking System

The ranking system provides utilities to rank professors by course or by domain/institution.

### Ranking Utilities (`ranking_utils.py`)

Core ranking functions that can be used by both Python scripts and TypeScript:
- `rank_professors()` - Rank professors by metric (overall_rating, difficulty_rating, would_take_again)
- `aggregate_professor_ratings()` - Aggregate ratings across multiple courses
- `format_ranking_output()` - Format rankings for display

### Course-Level Rankings

**Python Script**: `query-professor-rankings.py`
- Get top/bottom professors for a specific course
- Supports all three metrics

**TypeScript Function**: `getTopBottomProfessors()` in `src/lib/supabase.ts`
- Frontend function for course-level rankings

### Domain-Level Rankings

**Python Script**: `generate-domain-rankings.py`
- Get top/bottom professors aggregated across all courses in a domain
- Supports MCP access (no env vars needed) or standalone mode

**TypeScript Function**: `getTopBottomProfessorsByDomain()` in `src/lib/supabase.ts`
- Frontend function for domain-level rankings

### Usage Examples

```bash
# Course-level rankings (Python)
python scripts/query-professor-rankings.py fin5521 --metric overall_rating --top-n 5

# Domain-level rankings (Python)
python scripts/generate-domain-rankings.py Finance ESG-UQAM --metric overall_rating --top-n 5

# All metrics for a domain
python scripts/generate-domain-rankings.py Finance ESG-UQAM --all-metrics

# All domains at an institution
python scripts/generate-domain-rankings.py --all-domains --metric overall_rating
```

### TypeScript Usage

```typescript
// Course-level
import { getTopBottomProfessors } from '@/lib/supabase';
const { top, bottom } = await getTopBottomProfessors('fin5521', 'overall_rating', 5);

// Domain-level
import { getTopBottomProfessorsByDomain } from '@/lib/supabase';
const { top, bottom, courses } = await getTopBottomProfessorsByDomain('Finance', 'ESG-UQAM', 'overall_rating', 5);
```

---

## Professor Ratings Fetch Script

**File**: `fetch-professor-ratings.py`

Fetches professor ratings from RateMyProfessor and stores them in Supabase.

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment file:**
   ```bash
   cp scripts/.env.example scripts/.env
   ```
   Then edit `scripts/.env` and add your Supabase credentials.

3. **Create professor mapping CSV:**
   ```bash
   cp scripts/professor_mapping.csv.example scripts/professor_mapping.csv
   ```
   Then edit `scripts/professor_mapping.csv` with your course-to-professor mappings.

### CSV Format

The `professor_mapping.csv` file should have the following format:

```csv
domain,professor_name,institution
Finance,John Smith,ESG-UQAM
Finance,Jane Doe,ESG-UQAM
Comptabilité,Robert Johnson,ESG-UQAM
```

- `domain`: The domain/department name (must match the `domain` field in your `courses` table)
- `professor_name`: Full name as it appears on RateMyProfessor
- `institution`: Institution name (must match the `institution` field in your `courses` table)

**Note**: The script assumes that professors in a domain teach ALL courses in that domain. Each professor listed will be mapped to all courses in that domain at that institution.

### Usage

```bash
cd scripts
python fetch-professor-ratings.py
```

The script will:
1. Load professor mappings from CSV (grouped by domain and institution)
2. Fetch all active courses from Supabase
3. Group courses by (institution, domain) combinations
4. For each domain-institution group:
   - Find the school on RateMyProfessor
   - Search for all professors in that domain
   - Map each professor to ALL courses in that domain
   - Store ratings in the `professor_ratings` table

### Output

- Console logs showing progress
- `professor_ratings_fetch.log` file with detailed logs
- Summary statistics at the end

---

## Base64 to DOCX Decoder

A tool to decode base64 encoded strings and save them as .docx files.

### Usage

```bash
cd scripts
python decode-base64-to-docx.py "BASE64_STRING" output.docx
```

**Options:**
- Read from stdin: Use `-` as the base64 string argument
- Custom output path: Use `-o` or `--output` flag

**Examples:**
```bash
# From command line argument:
python decode-base64-to-docx.py "SGVsbG8gV29ybGQ=" output.docx

# From stdin:
echo "SGVsbG8gV29ybGQ=" | python decode-base64-to-docx.py - output.docx

# Interactive mode:
python decode-base64-to-docx.py - output.docx
# (then paste your base64 string and press Ctrl+D or Ctrl+Z)
```

---

## Notes

- Most scripts require OpenAI API key in `.env` file
- Scripts that use MCP Supabase access don't need database credentials
- All content generation is in French
- Content format is Markdown
