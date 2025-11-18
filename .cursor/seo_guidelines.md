# 2025 Fast-Acting SEO Checklist (Tutoring Sites / Programmatic SEO)

A tight, up-to-date (Nov 2025) checklist that prioritizes what moves rankings quickest and avoids current penalties.

---

## 0) Non-negotiables (ship these first)
- Match searcher intent; fully satisfy the query (no doorway/thin pages).
- Avoid “scaled content abuse”: programmatic pages must be truly unique.
- No “site reputation abuse” (parasite SEO). Keep everything on-brand and editorially controlled.

---

## 1) Crawl, index, basics (week 1)
- Exactly **one canonical URL per intent**; use `<link rel="canonical">` consistently.
- `robots.txt`: block only what should never index; add `Sitemap:` line(s).
- XML sitemaps: fresh `lastmod`, segmented if large (e.g., universities/programs/courses).
- Titles ≤ 60 chars, compelling and unique; meta descriptions ≤ 155 chars, user-centric.
- Add breadcrumbs (UI + JSON-LD). Implement “Site name” markup so the right brand renders on SERP.

---

## 2) Speed & UX (week 1–2)
- Hit Core Web Vitals on money pages:
  - **LCP ≤ 2.5s**
  - **CLS ≤ 0.1**
  - **INP ≤ 200ms** (INP replaced FID in 2024)
- Optimize images (AVIF/WebP + correct `sizes`), inline critical CSS, minimize JS, lazy-load below-the-fold assets.

---

## 3) Content that ranks fast (repeatable playbook)
For each page template (University → Program → Course):
- **Above-the-fold clarity**: what you offer, for whom, outcome/CTA.
- **Unique proof/E-E-A-T**: pass rates, #students helped, tutor bios with credentials, real testimonials.
- **Original value**: solved sample problems, exam timelines, campus specifics, booking options.
- **FAQs**: write them for users; don’t rely on rich results (still useful for comprehension/AI, but snippets are limited).
- AI-assisted drafting is fine; require human subject-matter review and fact checks.

---

## 4) Structured data that still pays (2025)
- Use only if present on the page and accurate:
  - `Course`, `EducationalOrganization`, `LocalBusiness` (if local), `BreadcrumbList`, `Review`, and `FAQPage` (helpful even if no rich result).
- Skip chasing broad `HowTo`/site-wide `FAQ` rich result “quick wins” (deprioritized/limited).

---

## 5) Internal linking (instant wins)
- University → top Programs → top Courses with contextual anchors.
- “Next steps” blocks: sibling courses, tutor profiles, booking CTA.
- Keep 3–6 prominent internal links above the fold; ensure breadcrumb trails.

---

## 6) Off-page that works quickly
- **Local signals**: Google Business Profile (proper categories, services, booking URL), consistent NAP, key local/campus citations.
- **Topical PR**: publish original study guides/exam checklists; pitch student newspapers, department blogs, clubs.
- **Links**: prioritize relevant edu/local links; use disavow only for manual actions or clear link schemes.

---

## 7) Programmatic SEO (safe mode)
- Each page must include:
  - Unique intro and entity-rich specifics (course code, credits, semester timing, textbook).
  - Tutor quotes or micro-case studies (original).
  - At least one original asset (table/checklist/mini-calculator).
- Dedupe before publish (similarity checks); throttle indexation (e.g., 50–100 pages/day).
- Canonicalize duplicates (e.g., same course across multiple programs → one canonical).

---

## 8) SERP features reality check (2025)
- Expect fewer broad “quick-win” rich results; focus on the main blue link via usefulness.
- Keep feature markup honest; don’t over-schema content you don’t actually show.

---

## 9) Governance & QA (prevents future drops)
- Content policy: no thin/auto-spun pages; cite sources on fact-heavy claims; editor sign-off required.
- Maintain change logs; trigger on-demand revalidation after updates.
- Weekly checks: manual actions, crawl errors, CWV regressions, template variants losing position/rate after updates.

---

## 10) What not to waste time on
- Mass FAQ schema to force snippets (limited value in 2025).
- Disavow files unless you have a manual action or undeniable link scheme you can’t remove.

---

## Quick “Launch Week” Task List
1) Fix CWV on top 20 pages (LCP/CLS/INP).
2) Refresh titles/H1s to match intent; add unique descriptors.
3) Add Course/Organization/Breadcrumb JSON-LD to templates.
4) Publish 30 high-quality programmatic pages (fully unique + original value); batch the rest.
5) Strengthen internal links (University → Program → Course and back).
6) Secure 5–10 relevant links (dept pages, student clubs, local edu blogs).
7) Submit updated sitemaps; verify in GSC; monitor coverage and queries.
8) Stand up dashboards: impressions/CTR by template, CWV trends, indexation velocity.

---

## Implementation Notes for Next.js + Supabase
- **Data model**: clean academic tables (`universities`, `programs`, `courses`) + a publishable `seo_pages` table (title/H1/meta/intro_md/faq/json_ld/og_image_url/is_indexable).
- **Rendering**: SSG with ISR; on-demand revalidate via `/api/revalidate` when `seo_pages` changes.
- **Sitemaps**: DB-driven with `lastmod`; segment by type if >10k URLs.
- **OG Images**: generate per page (Satori/Resvg) and store URL.
- **QC**: enforce minimum word counts (u≥600, p≥800, c≥900), required original asset, and similarity thresholds before `is_indexable=true`.

---

## KPI Dashboard (weekly)
- Index coverage by page type.
- Impressions, CTR, avg position (by template variant).
- CWV pass rate (per template + per device).
- Crawl budget health (pages discovered vs indexed; time to index).
- New/removed links; manual actions; 404/soft 404 trendlines.

---
