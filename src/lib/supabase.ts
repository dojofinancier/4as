import { createClient } from '@supabase/supabase-js';
import { CourseAvailability, CourseBlogPost, CourseBlogPostCreate, CourseBlogPostUpdate, CourseBlogPostWithCourse, ProfessorRating, GeneralArticle, GeneralArticleCreate, GeneralArticleUpdate } from '../types';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabasePublishableKey) {
  console.error('Missing Supabase environment variables:', {
    hasUrl: !!supabaseUrl,
    hasKey: !!supabasePublishableKey,
    url: supabaseUrl ? `${supabaseUrl.substring(0, 20)}...` : 'missing',
    key: supabasePublishableKey ? `${supabasePublishableKey.substring(0, 20)}...` : 'missing'
  });
  throw new Error('Missing Supabase environment variables. Please check your .env file.');
}

// Create Supabase client with proper configuration for anonymous access
export const supabase = createClient(supabaseUrl, supabasePublishableKey, {
  auth: {
    autoRefreshToken: false, // Not needed for anonymous access
    persistSession: false, // Not needed for anonymous access
    detectSessionInUrl: false
  }
});

export async function searchCourses(query: string) {
  if (!query.trim()) return [];
  
  // Verify environment variables are set
  if (!import.meta.env.VITE_SUPABASE_URL || !import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY) {
    console.error('Supabase environment variables are not set');
    return [];
  }
  
  const { data, error } = await supabase
    .from('courses')
    .select('id, code, title_fr, slug, institution, active')
    .or(`title_fr.ilike.%${query}%,code.ilike.%${query}%`)
    .limit(10);
    
  if (error) {
    console.error('Error searching courses:', error);
    console.error('Error details:', {
      message: error.message,
      details: error.details,
      hint: error.hint,
      code: error.code
    });
    return [];
  }
  
  return data || [];
}

export async function checkCourseAvailability(courseCode: string): Promise<CourseAvailability> {
  try {
    const url = `https://app.carredastutorat.com/api/check-course-availability?courseCode=${encodeURIComponent(courseCode)}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add mode: 'cors' to get better error messages
      mode: 'cors',
    });
    
    if (!response.ok) {
      console.warn(`Availability check API returned status ${response.status} for course ${courseCode}`);
      return { available: false, slug: null, tutorsCount: 0 };
    }
    
    return await response.json();
  } catch (error) {
    // Handle CORS and network errors gracefully
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.warn('Availability check failed (CORS or network error). This is expected in development. Falling back to unavailable state.');
      console.warn('Note: The app API at app.carredastutorat.com needs to allow CORS from the landing page domain.');
    } else {
      console.error('Error checking course availability:', error);
    }
    // Return unavailable state on any error (graceful degradation)
    return { available: false, slug: null, tutorsCount: 0 };
  }
}

// Blog Post Functions

/**
 * Generate SEO-friendly slug from course title
 * Example: "Analyse des valeurs mobilières I" -> "analyse-des-valeurs-mobilieres-i"
 */
export function generateBlogSlug(title: string, code?: string): string {
  return title
    .toLowerCase()
    .normalize('NFD') // Normalize to decomposed form for handling accents
    .replace(/[\u0300-\u036f]/g, '') // Remove diacritical marks
    .replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric with hyphens
    .replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens
    .substring(0, 100) // Limit length
    + (code ? `-${code.toLowerCase().replace(/[^a-z0-9]+/g, '-')}` : '');
}

/**
 * Fetch a published blog post by blog slug (SEO-friendly) or course slug (fallback)
 */
export async function getBlogPostBySlug(slug: string): Promise<CourseBlogPostWithCourse | null> {
  try {
    // First try to find by blog_slug (SEO-friendly), then fallback to course_slug
    const { data: blogPost, error: blogError } = await supabase
      .from('course_blog_posts')
      .select('*')
      .or(`blog_slug.eq.${slug},course_slug.eq.${slug}`)
      .eq('published', true)
      .single();

    if (blogError) {
      if (blogError.code === 'PGRST116') {
        // No rows returned
        return null;
      }
      console.error('Error fetching blog post:', blogError);
      return null;
    }

    if (!blogPost) {
      return null;
    }

    // Fetch course data
    const { data: course, error: courseError } = await supabase
      .from('courses')
      .select('id, title_fr, code, slug, institution, domain, description_fr, active')
      .eq('slug', slug)
      .single();

    if (courseError) {
      console.error('Error fetching course data:', courseError);
    }

    // Fetch professor ratings for this course
    const { data: ratings, error: ratingsError } = await supabase
      .from('professor_ratings')
      .select('*')
      .eq('course_slug', slug)
      .order('overall_rating', { ascending: false, nullsFirst: false });

    if (ratingsError) {
      console.error('Error fetching professor ratings:', ratingsError);
    }

    return {
      ...blogPost,
      course: course || undefined,
      professor_ratings: ratings || []
    } as CourseBlogPostWithCourse;
  } catch (error) {
    console.error('Error in getBlogPostBySlug:', error);
    return null;
  }
}

/**
 * Fetch all published blog posts (for blog index/listing)
 */
export async function getAllPublishedBlogPosts(limit: number = 50): Promise<CourseBlogPost[]> {
  try {
    const { data, error } = await supabase
      .from('course_blog_posts')
      .select('*')
      .eq('published', true)
      .eq('is_indexable', true)
      .order('published_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching blog posts:', error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error('Error in getAllPublishedBlogPosts:', error);
    return [];
  }
}

/**
 * Search blog posts by title, course code, or keywords
 */
export async function searchBlogPosts(searchQuery: string, domain?: string, limit: number = 100): Promise<CourseBlogPost[]> {
  try {
    let query = supabase
      .from('course_blog_posts')
      .select('*')
      .eq('published', true);

    // Only filter by is_indexable if we want to show only indexable posts
    // For blog listing, we want to show all published posts
    // query = query.eq('is_indexable', true);

    if (searchQuery.trim()) {
      query = query.or(`title.ilike.%${searchQuery}%,course_code.ilike.%${searchQuery}%,excerpt.ilike.%${searchQuery}%`);
    }

    // Order by published_at, handling nulls last
    query = query.order('published_at', { ascending: false, nullsFirst: false }).limit(limit);

    const { data, error } = await query;

    if (error) {
      console.error('Error searching blog posts:', error);
      console.error('Error details:', error);
      return [];
    }

    console.log(`[searchBlogPosts] Found ${data?.length || 0} blog posts (searchQuery: "${searchQuery}", domain: ${domain})`);
    
    let results = (data || []) as CourseBlogPost[];

    // Filter by domain if specified (after fetching since domain is on courses table)
    if (domain && results.length > 0) {
      // Fetch course domains for the blog posts
      const courseSlugs = [...new Set(results.map((bp) => bp.course_slug))];
      const { data: courses } = await supabase
        .from('courses')
        .select('slug, domain')
        .in('slug', courseSlugs);

      const domainMap = new Map(courses?.map((c: any) => [c.slug, c.domain]) || []);
      results = results.filter((bp) => domainMap.get(bp.course_slug) === domain);
    }

    return results;
  } catch (error) {
    console.error('Error in searchBlogPosts:', error);
    return [];
  }
}

/**
 * Search general articles by title, keywords, or tags
 */
export async function searchGeneralArticles(searchQuery: string, category?: string, limit: number = 100): Promise<GeneralArticle[]> {
  try {
    let query = supabase
      .from('general_articles')
      .select('*')
      .eq('published', true)
      .eq('is_indexable', true);

    if (searchQuery.trim()) {
      query = query.or(`title.ilike.%${searchQuery}%,excerpt.ilike.%${searchQuery}%`);
    }

    if (category) {
      query = query.eq('category', category);
    }

    query = query.order('published_at', { ascending: false }).limit(limit);

    const { data, error } = await query;

    if (error) {
      console.error('Error searching general articles:', error);
      return [];
    }

    let results = (data || []) as GeneralArticle[];

    // Filter by tags/keywords if search query provided
    if (searchQuery.trim() && results.length > 0) {
      const queryLower = searchQuery.toLowerCase();
      results = results.filter(article => {
        const titleMatch = article.title.toLowerCase().includes(queryLower);
        const excerptMatch = article.excerpt?.toLowerCase().includes(queryLower);
        const tagsMatch = article.tags?.some(tag => tag.toLowerCase().includes(queryLower));
        const keywordsMatch = article.keywords?.some(keyword => keyword.toLowerCase().includes(queryLower));
        return titleMatch || excerptMatch || tagsMatch || keywordsMatch;
      });
    }

    return results;
  } catch (error) {
    console.error('Error in searchGeneralArticles:', error);
    return [];
  }
}

/**
 * Get all unique domains from courses (for category filtering)
 */
export async function getAllDomains(): Promise<string[]> {
  try {
    const { data, error } = await supabase
      .from('courses')
      .select('domain')
      .not('domain', 'is', null)
      .eq('active', true);

    if (error) {
      console.error('Error fetching domains:', error);
      return [];
    }

    const domains = [...new Set((data || []).map((c: any) => c.domain).filter(Boolean))];
    return domains.sort();
  } catch (error) {
    console.error('Error in getAllDomains:', error);
    return [];
  }
}

/**
 * Get all unique categories from general articles
 */
export async function getAllArticleCategories(): Promise<string[]> {
  try {
    const { data, error } = await supabase
      .from('general_articles')
      .select('category')
      .eq('published', true)
      .not('category', 'is', null);

    if (error) {
      console.error('Error fetching categories:', error);
      return [];
    }

    const categories = [...new Set((data || []).map((a: any) => a.category).filter(Boolean))];
    return categories.sort();
  } catch (error) {
    console.error('Error in getAllArticleCategories:', error);
    return [];
  }
}

/**
 * Create a new blog post (requires service role key - for AI generation script)
 * Note: This function uses the public client, so it will only work if RLS allows it
 * For production, this should be called from a server-side script with service role key
 */
export async function createBlogPost(data: CourseBlogPostCreate): Promise<CourseBlogPost | null> {
  try {
    const { data: blogPost, error } = await supabase
      .from('course_blog_posts')
      .insert({
        ...data,
        published_at: data.published ? new Date().toISOString() : null
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating blog post:', error);
      return null;
    }

    return blogPost;
  } catch (error) {
    console.error('Error in createBlogPost:', error);
    return null;
  }
}

/**
 * Update an existing blog post (requires service role key - for AI generation script)
 * Note: This function uses the public client, so it will only work if RLS allows it
 * For production, this should be called from a server-side script with service role key
 */
export async function updateBlogPost(slug: string, data: CourseBlogPostUpdate): Promise<CourseBlogPost | null> {
  try {
    const updateData: any = { ...data };
    
    // Set published_at if being published for the first time
    if (data.published === true) {
      const { data: existing } = await supabase
        .from('course_blog_posts')
        .select('published_at')
        .eq('course_slug', slug)
        .single();
      
      if (existing && !existing.published_at) {
        updateData.published_at = new Date().toISOString();
      }
    }

    const { data: blogPost, error } = await supabase
      .from('course_blog_posts')
      .update(updateData)
      .eq('course_slug', slug)
      .select()
      .single();

    if (error) {
      console.error('Error updating blog post:', error);
      return null;
    }

    return blogPost;
  } catch (error) {
    console.error('Error in updateBlogPost:', error);
    return null;
  }
}

/**
 * Get professor ratings for a specific course
 */
export async function getProfessorRatingsByCourseSlug(slug: string): Promise<ProfessorRating[]> {
  try {
    const { data, error } = await supabase
      .from('professor_ratings')
      .select('*')
      .eq('course_slug', slug)
      .order('overall_rating', { ascending: false, nullsFirst: false });

    if (error) {
      console.error('Error fetching professor ratings:', error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error('Error in getProfessorRatingsByCourseSlug:', error);
    return [];
  }
}

/**
 * Get top N and bottom N professors for a course by a specific metric
 * 
 * @param slug Course slug
 * @param metric 'overall_rating', 'difficulty_rating', or 'would_take_again'
 * @param topN Number of top/bottom professors to return (default: 5)
 * @returns Object with 'top' and 'bottom' arrays of ProfessorRating
 */
export async function getTopBottomProfessors(
  slug: string,
  metric: 'overall_rating' | 'difficulty_rating' | 'would_take_again' = 'overall_rating',
  topN: number = 5
): Promise<{ top: ProfessorRating[]; bottom: ProfessorRating[] }> {
  try {
    // Fetch all ratings for this course with the metric
    const { data, error } = await supabase
      .from('professor_ratings')
      .select('*')
      .eq('course_slug', slug)
      .not(metric, 'is', null);

    if (error) {
      console.error('Error fetching professor ratings:', error);
      return { top: [], bottom: [] };
    }

    if (!data || data.length === 0) {
      return { top: [], bottom: [] };
    }

    // Sort by metric
    let sorted: ProfessorRating[];
    if (metric === 'difficulty_rating') {
      // Lower difficulty is better, so sort ascending
      sorted = [...data].sort((a, b) => {
        const aVal = a[metric] ?? 0;
        const bVal = b[metric] ?? 0;
        return aVal - bVal;
      });
    } else {
      // Higher rating is better, so sort descending
      sorted = [...data].sort((a, b) => {
        const aVal = a[metric] ?? 0;
        const bVal = b[metric] ?? 0;
        return bVal - aVal;
      });
    }

    // Get top N and bottom N
    const top = sorted.slice(0, topN);
    const bottom = sorted.slice(-topN).reverse(); // Reverse to show worst first

    return { top, bottom };
  } catch (error) {
    console.error('Error in getTopBottomProfessors:', error);
    return { top: [], bottom: [] };
  }
}

/**
 * Get top/bottom professors aggregated by domain/institution.
 * Aggregates ratings across all courses in the domain.
 */
export interface DomainProfessorRanking {
  professor_name: string;
  avg_overall_rating?: number;
  avg_difficulty_rating?: number;
  avg_would_take_again?: number;
  total_ratings: number;
  courses_count: number;
  course_slugs: string[];
}

export async function getTopBottomProfessorsByDomain(
  domain: string,
  institution: string,
  metric: 'overall_rating' | 'difficulty_rating' | 'would_take_again' = 'overall_rating',
  topN: number = 5
): Promise<{ top: DomainProfessorRanking[]; bottom: DomainProfessorRanking[]; courses: any[] }> {
  try {
    // First, get all courses in this domain/institution
    const { data: courses, error: coursesError } = await supabase
      .from('courses')
      .select('slug, code, title_fr')
      .eq('active', true)
      .eq('domain', domain)
      .eq('institution', institution);

    if (coursesError) {
      console.error('Error fetching courses:', coursesError);
      return { top: [], bottom: [], courses: [] };
    }

    if (!courses || courses.length === 0) {
      return { top: [], bottom: [], courses: [] };
    }

    const courseSlugs = courses.map(c => c.slug).filter(Boolean);

    if (courseSlugs.length === 0) {
      return { top: [], bottom: [], courses };
    }

    // Fetch all ratings for courses in this domain
    const { data: ratings, error: ratingsError } = await supabase
      .from('professor_ratings')
      .select('*')
      .in('course_slug', courseSlugs)
      .not(metric, 'is', null);

    if (ratingsError) {
      console.error('Error fetching professor ratings:', ratingsError);
      return { top: [], bottom: [], courses };
    }

    if (!ratings || ratings.length === 0) {
      return { top: [], bottom: [], courses };
    }

    // Aggregate by professor name
    const professorAggregates = new Map<string, {
      professor_name: string;
      overall_ratings: number[];
      difficulty_ratings: number[];
      would_take_again_ratings: number[];
      total_ratings: number;
      courses_count: number;
      course_slugs: Set<string>;
    }>();

    for (const rating of ratings) {
      const profName = rating.professor_name;
      if (!profName) continue;

      if (!professorAggregates.has(profName)) {
        professorAggregates.set(profName, {
          professor_name: profName,
          overall_ratings: [],
          difficulty_ratings: [],
          would_take_again_ratings: [],
          total_ratings: 0,
          courses_count: 0,
          course_slugs: new Set(),
        });
      }

      const agg = professorAggregates.get(profName)!;
      
      if (rating.overall_rating != null) agg.overall_ratings.push(rating.overall_rating);
      if (rating.difficulty_rating != null) agg.difficulty_ratings.push(rating.difficulty_rating);
      if (rating.would_take_again != null) agg.would_take_again_ratings.push(rating.would_take_again);
      
      agg.total_ratings += rating.total_ratings || 0;
      agg.courses_count += 1;
      agg.course_slugs.add(rating.course_slug);
    }

    // Calculate averages and create ranking objects
    const professorRankings: DomainProfessorRanking[] = [];
    for (const [name, agg] of professorAggregates.entries()) {
      const ranking: DomainProfessorRanking = {
        professor_name: name,
        avg_overall_rating: agg.overall_ratings.length > 0
          ? agg.overall_ratings.reduce((a, b) => a + b, 0) / agg.overall_ratings.length
          : undefined,
        avg_difficulty_rating: agg.difficulty_ratings.length > 0
          ? agg.difficulty_ratings.reduce((a, b) => a + b, 0) / agg.difficulty_ratings.length
          : undefined,
        avg_would_take_again: agg.would_take_again_ratings.length > 0
          ? agg.would_take_again_ratings.reduce((a, b) => a + b, 0) / agg.would_take_again_ratings.length
          : undefined,
        total_ratings: agg.total_ratings,
        courses_count: agg.courses_count,
        course_slugs: Array.from(agg.course_slugs),
      };
      professorRankings.push(ranking);
    }

    // Filter by metric and sort
    const metricKey = `avg_${metric}` as keyof DomainProfessorRanking;
    const filtered = professorRankings.filter(p => p[metricKey] != null);

    let sorted: DomainProfessorRanking[];
    if (metric === 'difficulty_rating') {
      // Lower difficulty is better
      sorted = [...filtered].sort((a, b) => {
        const aVal = (a[metricKey] as number) ?? Infinity;
        const bVal = (b[metricKey] as number) ?? Infinity;
        return aVal - bVal;
      });
    } else {
      // Higher rating is better
      sorted = [...filtered].sort((a, b) => {
        const aVal = (a[metricKey] as number) ?? 0;
        const bVal = (b[metricKey] as number) ?? 0;
        return bVal - aVal;
      });
    }

    // Get top N and bottom N
    const top = sorted.slice(0, topN);
    const bottom = sorted.slice(-topN).reverse(); // Reverse to show worst first

    return { top, bottom, courses };
  } catch (error) {
    console.error('Error in getTopBottomProfessorsByDomain:', error);
    return { top: [], bottom: [], courses: [] };
  }
}

// General Article Functions

/**
 * Generate SEO-friendly slug from article title
 */
export function generateArticleSlug(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .substring(0, 100);
}

/**
 * Fetch a published general article by slug
 */
export async function getGeneralArticleBySlug(slug: string): Promise<GeneralArticle | null> {
  try {
    const { data, error } = await supabase
      .from('general_articles')
      .select('*')
      .eq('slug', slug)
      .eq('published', true)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      console.error('Error fetching general article:', error);
      return null;
    }

    return data as GeneralArticle;
  } catch (error) {
    console.error('Error in getGeneralArticleBySlug:', error);
    return null;
  }
}

/**
 * Fetch all published general articles (for listings and related articles)
 */
export async function getAllPublishedGeneralArticles(limit: number = 50, category?: string): Promise<GeneralArticle[]> {
  try {
    let query = supabase
      .from('general_articles')
      .select('*')
      .eq('published', true)
      .eq('is_indexable', true)
      .order('published_at', { ascending: false })
      .limit(limit);

    if (category) {
      query = query.eq('category', category);
    }

    const { data, error } = await query;

    if (error) {
      console.error('Error fetching general articles:', error);
      return [];
    }

    return (data || []) as GeneralArticle[];
  } catch (error) {
    console.error('Error in getAllPublishedGeneralArticles:', error);
    return [];
  }
}

/**
 * Get related articles for a given article
 */
export async function getRelatedArticles(articleId: string, limit: number = 5): Promise<GeneralArticle[]> {
  try {
    // First get the article to find its related_articles array
    const { data: article, error: articleError } = await supabase
      .from('general_articles')
      .select('related_articles')
      .eq('id', articleId)
      .single();

    if (articleError || !article || !article.related_articles || article.related_articles.length === 0) {
      return [];
    }

    // Fetch the related articles
    const { data, error } = await supabase
      .from('general_articles')
      .select('*')
      .in('id', article.related_articles)
      .eq('published', true)
      .limit(limit);

    if (error) {
      console.error('Error fetching related articles:', error);
      return [];
    }

    return (data || []) as GeneralArticle[];
  } catch (error) {
    console.error('Error in getRelatedArticles:', error);
    return [];
  }
}

/**
 * Get articles for internal linking (based on category, tags, keywords)
 */
export async function getArticlesForLinking(category?: string, tags?: string[], keywords?: string[]): Promise<GeneralArticle[]> {
  try {
    let query = supabase
      .from('general_articles')
      .select('id, slug, title, excerpt, tags, keywords, category')
      .eq('published', true);

    if (category) {
      query = query.eq('category', category);
    }

    if (tags && tags.length > 0) {
      query = query.overlaps('tags', tags);
    }

    if (keywords && keywords.length > 0) {
      query = query.overlaps('keywords', keywords);
    }

    const { data, error } = await query.limit(100);

    if (error) {
      console.error('Error fetching articles for linking:', error);
      return [];
    }

    return (data || []) as GeneralArticle[];
  } catch (error) {
    console.error('Error in getArticlesForLinking:', error);
    return [];
  }
}

/**
 * Get related course blog posts (by domain/institution)
 */
export async function getRelatedCourseBlogPosts(
  currentCourseSlug: string,
  domain?: string,
  institution?: string,
  limit: number = 5
): Promise<CourseBlogPost[]> {
  try {
    // First get the current course to find domain/institution
    const { data: currentCourse } = await supabase
      .from('courses')
      .select('domain, institution')
      .eq('slug', currentCourseSlug)
      .single();

    const courseDomain = domain || currentCourse?.domain;
    const courseInstitution = institution || currentCourse?.institution;

    let query = supabase
      .from('course_blog_posts')
      .select('*, courses!inner(domain, institution)')
      .eq('published', true)
      .eq('is_indexable', true)
      .neq('course_slug', currentCourseSlug);

    // Filter by domain if available
    if (courseDomain) {
      query = query.eq('courses.domain', courseDomain);
    }

    // Filter by institution if available
    if (courseInstitution) {
      query = query.eq('courses.institution', courseInstitution);
    }

    const { data, error } = await query
      .order('published_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching related course blog posts:', error);
      return [];
    }

    return (data || []) as CourseBlogPost[];
  } catch (error) {
    console.error('Error in getRelatedCourseBlogPosts:', error);
    return [];
  }
}

/**
 * Create a new general article (for AI generation workflow)
 */
export async function createGeneralArticle(data: GeneralArticleCreate): Promise<GeneralArticle | null> {
  try {
    const { data: article, error } = await supabase
      .from('general_articles')
      .insert({
        ...data,
        published_at: data.published ? new Date().toISOString() : null
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating general article:', error);
      return null;
    }

    return article as GeneralArticle;
  } catch (error) {
    console.error('Error in createGeneralArticle:', error);
    return null;
  }
}

/**
 * Update an existing general article
 */
export async function updateGeneralArticle(slug: string, data: GeneralArticleUpdate): Promise<GeneralArticle | null> {
  try {
    const updateData: any = { ...data };
    
    // Set published_at if being published for the first time
    if (data.published === true) {
      const { data: existing } = await supabase
        .from('general_articles')
        .select('published_at')
        .eq('slug', slug)
        .single();
      
      if (existing && !existing.published_at) {
        updateData.published_at = new Date().toISOString();
      }
    }

    const { data: article, error } = await supabase
      .from('general_articles')
      .update(updateData)
      .eq('slug', slug)
      .select()
      .single();

    if (error) {
      console.error('Error updating general article:', error);
      return null;
    }

    return article as GeneralArticle;
  } catch (error) {
    console.error('Error in updateGeneralArticle:', error);
    return null;
  }
}