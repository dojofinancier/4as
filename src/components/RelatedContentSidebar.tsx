/**
 * Related Content Sidebar Component
 * Displays related courses/articles above the fold
 */
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { BookOpen, ArrowRight } from 'lucide-react';
import { getRelatedCourseBlogPosts, getRelatedArticles } from '../lib/supabase';
import type { CourseBlogPost, GeneralArticle } from '../types';

interface RelatedContentSidebarProps {
  type: 'course' | 'article';
  courseSlug?: string;
  articleId?: string;
  domain?: string;
  institution?: string;
  limit?: number;
}

export function RelatedContentSidebar({
  type,
  courseSlug,
  articleId,
  domain,
  institution,
  limit = 5,
}: RelatedContentSidebarProps) {
  // Fetch related course blog posts
  const { data: relatedCourses } = useQuery({
    queryKey: ['relatedCourses', courseSlug, domain, institution],
    queryFn: async () => {
      if (type === 'course' && courseSlug) {
        return await getRelatedCourseBlogPosts(courseSlug, domain, institution, limit);
      }
      return [];
    },
    enabled: type === 'course' && !!courseSlug,
    staleTime: 5 * 60 * 1000,
  });

  // Fetch related articles
  const { data: relatedArticles } = useQuery({
    queryKey: ['relatedArticles', articleId],
    queryFn: async () => {
      if (type === 'article' && articleId) {
        return await getRelatedArticles(articleId, limit);
      }
      return [];
    },
    enabled: type === 'article' && !!articleId,
    staleTime: 5 * 60 * 1000,
  });

  const hasContent = 
    (type === 'course' && relatedCourses && relatedCourses.length > 0) ||
    (type === 'article' && relatedArticles && relatedArticles.length > 0);

  if (!hasContent) {
    return null;
  }

  return (
    <aside className="w-full lg:w-80 lg:sticky lg:top-4 h-fit">
      <div className="bg-card rounded-2xl shadow-sm border border-border p-6">
        <h2 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
          <BookOpen className="h-5 w-5" />
          {type === 'course' ? 'Cours similaires' : 'Articles connexes'}
        </h2>
        
        <ul className="space-y-4">
          {type === 'course' && relatedCourses?.map((course: CourseBlogPost) => (
            <li key={course.id || course.course_slug}>
              <Link
                to={`/${course.blog_slug || course.course_slug}`}
                className="block group hover:bg-muted/50 rounded-lg p-3 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-2">
                      {course.title || course.course_code}
                    </h3>
                    {course.excerpt && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {course.excerpt}
                      </p>
                    )}
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary flex-shrink-0 mt-1 transition-colors" />
                </div>
              </Link>
            </li>
          ))}

          {type === 'article' && relatedArticles?.map((article: GeneralArticle) => (
            <li key={article.id}>
              <Link
                to={`/article/${article.slug}`}
                className="block group hover:bg-muted/50 rounded-lg p-3 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-2">
                      {article.title}
                    </h3>
                    {article.excerpt && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {article.excerpt}
                      </p>
                    )}
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary flex-shrink-0 mt-1 transition-colors" />
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}

