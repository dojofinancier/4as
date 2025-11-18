/**
 * Static sitemap generation script
 * Run this before building: node scripts/generate-sitemap.js
 * 
 * Generates:
 * - public/sitemap.xml (index sitemap)
 * - public/sitemap-courses.xml
 * - public/sitemap-articles.xml
 */

import { createClient } from '@supabase/supabase-js';
import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from .env file
function loadEnvFile() {
  const envPath = join(__dirname, '..', '.env');
  if (existsSync(envPath)) {
    const envContent = readFileSync(envPath, 'utf8');
    envContent.split('\n').forEach(line => {
      const trimmedLine = line.trim();
      if (trimmedLine && !trimmedLine.startsWith('#')) {
        const [key, ...valueParts] = trimmedLine.split('=');
        if (key && valueParts.length > 0) {
          const value = valueParts.join('=').replace(/^["']|["']$/g, ''); // Remove quotes
          process.env[key.trim()] = value.trim();
        }
      }
    });
  }
}

// Load .env file
loadEnvFile();

const BASE_URL = 'https://carredastutorat.com';

// Get Supabase credentials from environment
const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase environment variables');
  console.error('Please set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Escape XML special characters
 */
function escapeXml(unsafe) {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Format date for sitemap (ISO 8601)
 */
function formatDate(date) {
  if (!date) return new Date().toISOString();
  return new Date(date).toISOString();
}

/**
 * Generate XML sitemap entry
 */
function generateUrlEntry(loc, lastmod, changefreq = 'monthly', priority = '0.8') {
  return `  <url>
    <loc>${escapeXml(loc)}</loc>
    <lastmod>${formatDate(lastmod)}</lastmod>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`;
}

/**
 * Generate sitemap XML
 */
function generateSitemap(urls) {
  const urlEntries = urls.map(({ loc, lastmod, changefreq, priority }) =>
    generateUrlEntry(loc, lastmod, changefreq, priority)
  ).join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlEntries}
</urlset>`;
}

/**
 * Generate sitemap index XML
 */
function generateSitemapIndex(sitemaps) {
  const sitemapEntries = sitemaps.map(({ loc, lastmod }) =>
    `  <sitemap>
    <loc>${escapeXml(loc)}</loc>
    <lastmod>${formatDate(lastmod)}</lastmod>
  </sitemap>`
  ).join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapEntries}
</sitemapindex>`;
}

/**
 * Fetch all published course blog posts
 */
async function fetchCourseBlogPosts() {
  console.log('Fetching course blog posts...');
  const { data, error } = await supabase
    .from('course_blog_posts')
    .select('blog_slug, course_slug, updated_at, published_at, is_indexable, published')
    .eq('published', true)
    .eq('is_indexable', true);

  if (error) {
    console.error('Error fetching course blog posts:', error);
    return [];
  }

  return data || [];
}

/**
 * Fetch all published general articles
 */
async function fetchGeneralArticles() {
  console.log('Fetching general articles...');
  const { data, error } = await supabase
    .from('general_articles')
    .select('slug, updated_at, published_at, is_indexable, published')
    .eq('published', true)
    .eq('is_indexable', true);

  if (error) {
    console.error('Error fetching general articles:', error);
    return [];
  }

  return data || [];
}

/**
 * Generate course blog posts sitemap
 */
async function generateCoursesSitemap() {
  const blogPosts = await fetchCourseBlogPosts();
  
  const urls = blogPosts.map(post => ({
    loc: `${BASE_URL}/${post.blog_slug || post.course_slug}`,
    lastmod: post.updated_at || post.published_at,
    changefreq: 'monthly',
    priority: '0.8',
  }));

  // Add static pages
  urls.unshift({
    loc: BASE_URL,
    lastmod: new Date(),
    changefreq: 'weekly',
    priority: '1.0',
  });

  urls.push({
    loc: `${BASE_URL}/devenez-tuteur`,
    lastmod: new Date(),
    changefreq: 'monthly',
    priority: '0.7',
  });

  const sitemapXml = generateSitemap(urls);
  const filePath = join(__dirname, '..', 'public', 'sitemap-courses.xml');
  writeFileSync(filePath, sitemapXml, 'utf8');
  console.log(`✓ Generated sitemap-courses.xml with ${urls.length} URLs`);
  
  return {
    loc: `${BASE_URL}/sitemap-courses.xml`,
    lastmod: new Date(),
  };
}

/**
 * Generate general articles sitemap
 */
async function generateArticlesSitemap() {
  const articles = await fetchGeneralArticles();
  
  const urls = articles.map(article => ({
    loc: `${BASE_URL}/article/${article.slug}`,
    lastmod: article.updated_at || article.published_at,
    changefreq: 'monthly',
    priority: '0.7',
  }));

  const sitemapXml = generateSitemap(urls);
  const filePath = join(__dirname, '..', 'public', 'sitemap-articles.xml');
  writeFileSync(filePath, sitemapXml, 'utf8');
  console.log(`✓ Generated sitemap-articles.xml with ${urls.length} URLs`);
  
  return {
    loc: `${BASE_URL}/sitemap-articles.xml`,
    lastmod: new Date(),
  };
}

/**
 * Generate main sitemap index file
 */
function generateMainSitemapIndex(coursesSitemap, articlesSitemap) {
  const sitemaps = [coursesSitemap, articlesSitemap];
  const sitemapIndexXml = generateSitemapIndex(sitemaps);
  const filePath = join(__dirname, '..', 'public', 'sitemap.xml');
  writeFileSync(filePath, sitemapIndexXml, 'utf8');
  console.log(`✓ Generated sitemap.xml (index)`);
}

/**
 * Main function
 */
async function main() {
  console.log('Generating sitemaps...\n');
  
  try {
    const coursesSitemap = await generateCoursesSitemap();
    const articlesSitemap = await generateArticlesSitemap();
    generateMainSitemapIndex(coursesSitemap, articlesSitemap);
    
    console.log('\n✓ All sitemaps generated successfully!');
  } catch (error) {
    console.error('Error generating sitemaps:', error);
    process.exit(1);
  }
}

main();

