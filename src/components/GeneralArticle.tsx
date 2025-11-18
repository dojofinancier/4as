import { useParams, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import { BookOpen, ArrowRight, ExternalLink, User } from 'lucide-react';
import { getGeneralArticleBySlug, getRelatedArticles } from '../lib/supabase';
import type { GeneralArticle } from '../types';
import { ArticleCourseSearch } from './ArticleCourseSearch';
import { truncateTitle, truncateMetaDescription, getOrganizationSchema, getBreadcrumbSchema } from '../lib/seo';
import { Footer } from './Footer';
import { RelatedContentSidebar } from './RelatedContentSidebar';
import { Logo } from './Logo';

export function GeneralArticle() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  // Use React Query for caching and better data fetching
  const { data: article, isLoading: loading, error: queryError } = useQuery({
    queryKey: ['generalArticle', slug],
    queryFn: async () => {
      if (!slug) {
        throw new Error('Slug manquant');
      }
      const post = await getGeneralArticleBySlug(slug);
      if (!post) {
        throw new Error('Article non trouvé');
      }
      return post;
    },
    enabled: !!slug,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch related articles
  const { data: relatedArticles } = useQuery({
    queryKey: ['relatedArticles', article?.id],
    queryFn: async () => {
      if (!article?.id) return [];
      return await getRelatedArticles(article.id, 5);
    },
    enabled: !!article?.id,
    staleTime: 5 * 60 * 1000,
  });

  const error = queryError ? (queryError instanceof Error ? queryError.message : 'Erreur lors du chargement de l\'article') : null;

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="max-w-2xl w-full text-center">
          <h1 className="text-3xl font-bold text-foreground mb-4">Article non trouvé</h1>
          <p className="text-muted-foreground mb-8">{error || 'L\'article que vous recherchez n\'existe pas.'}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-8 rounded-xl transition-colors"
          >
            Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  // Generate canonical URL
  const canonicalUrl = `${window.location.origin}/article/${article.slug}`;

  // Prepare meta description (truncated to ≤155 chars)
  const metaDescriptionRaw = article.meta_description || article.excerpt || 
    `Article sur ${article.title} - Carré d'As Tutorat`;
  const metaDescription = truncateMetaDescription(metaDescriptionRaw);

  // Prepare title (truncated to ≤60 chars)
  const pageTitleRaw = article.h1 || article.title || "Article - Carré d'As Tutorat";
  const pageTitle = truncateTitle(pageTitleRaw);

  // Prepare Open Graph image
  const ogImage = article.featured_image_url || undefined;

  // Generate base URL
  const baseUrl = window.location.origin;

  // Generate JSON-LD structured data
  const jsonLd = article.json_ld || {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: pageTitle,
    description: metaDescription,
    image: ogImage,
    author: {
      '@type': 'Organization',
      name: "Carré d'As Tutorat",
    },
    publisher: {
      '@type': 'Organization',
      name: "Carré d'As Tutorat",
      logo: {
        '@type': 'ImageObject',
        url: `${baseUrl}/dark_logo_high.png`,
      },
    },
    datePublished: article.published_at || article.created_at,
    dateModified: article.updated_at,
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': canonicalUrl,
    },
    articleSection: article.category,
    keywords: article.keywords.join(', '),
  };

  // Generate Organization schema
  const organizationSchema = getOrganizationSchema(baseUrl);

  // Generate BreadcrumbList schema
  const breadcrumbSchema = getBreadcrumbSchema([
    { name: "Accueil", url: baseUrl },
    { name: "Article", url: `${baseUrl}/article` },
    { name: pageTitleRaw, url: canonicalUrl },
  ]);

  return (
    <div className="min-h-screen bg-background">
      {/* SEO Meta Tags using react-helmet-async */}
      <Helmet>
        <title>{pageTitle}</title>
        <meta name="description" content={metaDescription} />
        <link rel="canonical" href={canonicalUrl} />
        
        {/* Open Graph Tags */}
        <meta property="og:type" content="article" />
        <meta property="og:title" content={pageTitle} />
        <meta property="og:description" content={metaDescription} />
        <meta property="og:url" content={canonicalUrl} />
        <meta property="og:image" content={ogImage} />
        <meta property="og:site_name" content="Carré d'As Tutorat" />
        {article.published_at && (
          <meta property="article:published_time" content={article.published_at} />
        )}
        {article.updated_at && (
          <meta property="article:modified_time" content={article.updated_at} />
        )}
        {article.category && (
          <meta property="article:section" content={article.category} />
        )}
        {article.tags.length > 0 && (
          <meta property="article:tag" content={article.tags.join(', ')} />
        )}
        
        {/* Twitter Card Tags */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={pageTitle} />
        <meta name="twitter:description" content={metaDescription} />
        {ogImage && <meta name="twitter:image" content={ogImage} />}
        
        {/* Additional SEO Tags */}
        <meta name="robots" content={article.is_indexable ? "index, follow" : "noindex, nofollow"} />
        {article.author && <meta name="author" content={article.author} />}
      </Helmet>

      {/* Header with Logo */}
      <div className="absolute top-3 left-3 sm:top-4 sm:left-4 z-10">
        <Logo />
      </div>

      {/* Header Buttons */}
      <div className="absolute top-3 right-3 sm:top-4 sm:right-4 z-10 flex gap-2">
        <a
          href="https://app.carredastutorat.com/connexion"
          className="inline-flex items-center justify-center bg-primary hover:bg-primary/90 text-primary-foreground font-medium py-2 px-2 sm:px-4 rounded-lg text-xs sm:text-sm transition-all duration-200 shadow-sm hover:shadow-md"
          aria-label="Mon compte"
        >
          <User className="h-4 w-4 sm:hidden" />
          <span className="hidden sm:inline">MON COMPTE</span>
        </a>
        <a
          href="/devenez-tuteur"
          className="inline-block bg-card/80 hover:bg-card text-foreground/90 hover:text-foreground font-medium py-2 px-2 sm:px-4 rounded-lg text-xs sm:text-sm transition-all duration-200 shadow-sm hover:shadow-md border border-border"
        >
          <span className="hidden sm:inline">DEVENEZ TUTEURS</span>
          <span className="sm:hidden">TUTEURS</span>
        </a>
      </div>

      {/* Main Content */}
      <article className="max-w-7xl mx-auto px-4 pt-20 pb-12">
        {/* Article Header - Full Width */}
        <header className="mb-8">
          <div className="mb-4">
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground mb-2">
              {article.category && (
                <span className="flex items-center gap-1">
                  <BookOpen className="h-4 w-4" />
                  {article.category}
                </span>
              )}
              {article.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {article.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            {article.h1 || article.title}
          </h1>
          
          {article.excerpt && (
            <p className="text-xl text-muted-foreground leading-relaxed mb-6">
              {article.excerpt}
            </p>
          )}
        </header>

        {/* Content and Sidebar - Aligned */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Main Content */}
          <div className="flex-1">
            <div className="bg-card rounded-2xl shadow-sm border border-border p-8 mb-8">
          <div className="prose prose-lg max-w-none prose-headings:text-foreground prose-headings:font-bold prose-h1:hidden prose-h2:text-2xl prose-h2:mt-8 prose-h2:mb-4 prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3 prose-p:text-foreground/90 prose-p:mb-4 prose-p:leading-relaxed prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-strong:text-foreground prose-ul:text-foreground/90 prose-ol:text-foreground/90 prose-li:my-2">
            <ReactMarkdown
              components={{
                h1: () => null, // Remove H1 from content since it's already in the header
              }}
            >
              {article.content || ''}
            </ReactMarkdown>
          </div>
        </div>

        {/* Related Articles Section */}
        {relatedArticles && relatedArticles.length > 0 && (
          <div className="bg-card rounded-2xl shadow-sm border border-border p-8 mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-6">Articles connexes</h2>
            <ul className="space-y-3">
              {relatedArticles.map((related) => (
                <li key={related.id}>
                  <a
                    href={`/article/${related.slug}`}
                    className="text-primary hover:text-primary/90 font-medium text-lg flex items-center gap-2"
                  >
                    {related.title}
                    <ArrowRight className="h-4 w-4" />
                  </a>
                  {related.excerpt && (
                    <p className="text-muted-foreground text-sm mt-1">{related.excerpt}</p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* External Resources Section */}
        {article.external_links && Array.isArray(article.external_links) && article.external_links.length > 0 && (
          <div className="bg-card rounded-2xl shadow-sm border border-border p-8 mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-2">
              <ExternalLink className="h-6 w-6" />
              Ressources externes
            </h2>
            <ul className="space-y-3">
              {article.external_links.map((link, index) => (
                <li key={index}>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:text-primary/90 font-medium flex items-center gap-2"
                  >
                    {link.anchor_text}
                    <ExternalLink className="h-4 w-4" />
                  </a>
                  {link.description && (
                    <p className="text-muted-foreground text-sm mt-1">{link.description}</p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

            {/* CTA Section */}
            <div className="bg-primary rounded-2xl shadow-lg p-8 text-center text-primary-foreground">
              <h2 className="text-3xl font-bold mb-4">Besoin d'aide pour vos cours ?</h2>
              <p className="text-lg mb-8 opacity-90">
                Réservez une séance de tutorat avec un de nos tuteurs qualifiés
              </p>
              <div className="max-w-2xl mx-auto">
                <ArticleCourseSearch />
              </div>
            </div>
          </div>

          {/* Sidebar with related content - Aligned with content box */}
          <RelatedContentSidebar
            type="article"
            articleId={article.id}
            limit={5}
          />
        </div>

        {/* JSON-LD Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
        />
      </article>

      <Footer />
    </div>
  );
}

