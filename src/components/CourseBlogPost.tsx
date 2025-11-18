import { useParams, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import { BookOpen, Calendar, Users, Star, TrendingUp, TrendingDown, ArrowRight, User } from 'lucide-react';
import { getBlogPostBySlug } from '../lib/supabase';
import { CourseBlogPostWithCourse } from '../types';
import { truncateTitle, truncateMetaDescription, getOrganizationSchema, getBreadcrumbSchema } from '../lib/seo';
import { Footer } from './Footer';
import { RelatedContentSidebar } from './RelatedContentSidebar';
import { Logo } from './Logo';

export function CourseBlogPost() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  // Use React Query for caching and better data fetching
  const { data: blogPost, isLoading: loading, error: queryError } = useQuery({
    queryKey: ['blogPost', slug],
    queryFn: async () => {
      if (!slug) {
        throw new Error('Slug manquant');
      }
      const post = await getBlogPostBySlug(slug);
      if (!post) {
        throw new Error('Article de blog non trouvé');
      }
      return post;
    },
    enabled: !!slug,
    staleTime: 5 * 60 * 1000, // 5 minutes
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

  if (error || !blogPost) {
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

  const course = blogPost.course;
  const professorRatings = blogPost.professor_ratings || [];
  
  // Get top 3 and bottom 3 professors by overall_rating
  const top3Professors = professorRatings
    .filter(p => p.overall_rating != null)
    .sort((a, b) => (b.overall_rating || 0) - (a.overall_rating || 0))
    .slice(0, 3);
  
  const bottom3Professors = professorRatings
    .filter(p => p.overall_rating != null)
    .sort((a, b) => (a.overall_rating || 0) - (b.overall_rating || 0))
    .slice(0, 3);

  const isActive = course?.active ?? false;
  const reservationUrl = `https://app.carredastutorat.com/cours/${blogPost.course_slug}/reservation?code=${encodeURIComponent(blogPost.course_code)}&source=blog`;
  const questionnaireUrl = '/';

  // Generate canonical URL
  const canonicalUrl = blogPost.canonical_url || 
    (blogPost.blog_slug 
      ? `${window.location.origin}/${blogPost.blog_slug}`
      : `${window.location.origin}/${blogPost.course_slug}`);

  // Generate full URL for Open Graph
  const fullUrl = canonicalUrl;

  // Prepare meta description (truncated to ≤155 chars)
  const metaDescriptionRaw = blogPost.meta_description || blogPost.excerpt || 
    `Guide complet pour réussir le cours ${blogPost.course_code} - ${blogPost.course?.title_fr || ''}`;
  const metaDescription = truncateMetaDescription(metaDescriptionRaw);

  // Prepare title (truncated to ≤60 chars)
  const pageTitleRaw = blogPost.title || `${blogPost.course?.title_fr || 'Cours'} - Carré d'As Tutorat`;
  const pageTitle = truncateTitle(pageTitleRaw);

  // Prepare Open Graph image
  const ogImage = blogPost.og_image_url || blogPost.featured_image_url;

  // Generate base URL
  const baseUrl = window.location.origin;

  // Generate JSON-LD structured data
  const jsonLd = blogPost.json_ld || (() => {
    const baseJsonLd: any = {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: pageTitle,
      description: metaDescription,
      image: ogImage,
      author: {
        '@type': 'Organization',
        name: course?.institution || "Carré d'As Tutorat",
      },
      publisher: {
        '@type': 'Organization',
        name: "Carré d'As Tutorat",
        logo: {
          '@type': 'ImageObject',
          url: `${baseUrl}/dark_logo_high.png`,
        },
      },
      datePublished: blogPost.published_at || blogPost.created_at,
      dateModified: blogPost.updated_at,
      mainEntityOfPage: {
        '@type': 'WebPage',
        '@id': canonicalUrl,
      },
    };

    // Add course information if available
    if (course) {
      baseJsonLd.about = {
        '@type': 'Course',
        name: course.title_fr,
        courseCode: course.code,
        provider: {
          '@type': 'EducationalOrganization',
          name: course.institution,
        },
      };
    }

    return baseJsonLd;
  })();

  // Generate Organization schema
  const organizationSchema = getOrganizationSchema(baseUrl);

  // Generate BreadcrumbList schema
  const breadcrumbSchema = getBreadcrumbSchema([
    { name: "Accueil", url: baseUrl },
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
        <meta property="og:url" content={fullUrl} />
        <meta property="og:image" content={ogImage} />
        <meta property="og:site_name" content="Carré d'As Tutorat" />
        {blogPost.published_at && (
          <meta property="article:published_time" content={blogPost.published_at} />
        )}
        {blogPost.updated_at && (
          <meta property="article:modified_time" content={blogPost.updated_at} />
        )}
        {course?.institution && (
          <meta property="article:author" content={course.institution} />
        )}
        
        {/* Twitter Card Tags */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={pageTitle} />
        <meta name="twitter:description" content={metaDescription} />
        <meta name="twitter:image" content={ogImage} />
        
        {/* Additional SEO Tags */}
        <meta name="robots" content={blogPost.is_indexable ? "index, follow" : "noindex, nofollow"} />
        {blogPost.author && <meta name="author" content={blogPost.author} />}
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
        {/* Course Header - Full Width */}
        <header className="mb-8">
          {course && (
            <div className="mb-4">
              <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground mb-2">
                {course.institution && (
                  <span className="flex items-center gap-1">
                    <BookOpen className="h-4 w-4" />
                    {course.institution}
                  </span>
                )}
                {course.code && (
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    {course.code}
                  </span>
                )}
                {course.domain && (
                  <span className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {course.domain}
                  </span>
                )}
              </div>
            </div>
          )}
          
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            {blogPost.h1 || blogPost.title}
          </h1>
          
          {blogPost.excerpt && (
            <p className="text-xl text-muted-foreground leading-relaxed mb-6">
              {blogPost.excerpt}
            </p>
          )}

          {/* CTA Button - Above the fold */}
          {isActive && (
            <div className="mb-8">
              <a
                href={reservationUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-4 px-8 rounded-xl text-lg transition-colors shadow-lg hover:shadow-xl"
              >
                Réserver une séance de tutorat
                <ArrowRight className="h-5 w-5" />
              </a>
            </div>
          )}
          {!isActive && (
            <div className="mb-8">
              <a
                href={questionnaireUrl}
                className="inline-flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-4 px-8 rounded-xl text-lg transition-colors shadow-lg hover:shadow-xl"
              >
                Commencer le questionnaire
                <ArrowRight className="h-5 w-5" />
              </a>
            </div>
          )}
        </header>

        {/* Content and Sidebar - Aligned */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Main Content */}
          <div className="flex-1">
            {/* Professor Ratings Section - Always show if we have ratings */}
        {professorRatings.length > 0 && (
          <div className="bg-card rounded-2xl shadow-sm border border-border p-6 mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-4 flex items-center gap-2">
              <Star className="h-6 w-6 text-yellow-500" />
              Évaluations des professeurs
            </h2>
            
            {top3Professors.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-green-900 mb-3 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  Top 3 - Meilleures évaluations
                </h3>
                <div className="grid md:grid-cols-3 gap-4">
                  {top3Professors.map((prof, index) => (
                    <div key={prof.id || index} className="bg-green-50 rounded-lg p-4">
                      <p className="font-medium text-foreground mb-2">{prof.professor_name}</p>
                      {prof.overall_rating && (
                        <div className="flex items-center gap-2">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm font-semibold">{prof.overall_rating.toFixed(1)}/5.0</span>
                          {prof.total_ratings && (
                            <span className="text-sm text-muted-foreground">({prof.total_ratings} évaluations)</span>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {bottom3Professors.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-red-900 mb-3 flex items-center gap-2">
                  <TrendingDown className="h-5 w-5 text-red-600" />
                  Bottom 3 - Évaluations les plus basses
                </h3>
                <div className="grid md:grid-cols-3 gap-4">
                  {bottom3Professors.map((prof, index) => (
                    <div key={prof.id || index} className="bg-red-50 rounded-lg p-4">
                      <p className="font-medium text-foreground mb-2">{prof.professor_name}</p>
                      {prof.overall_rating && (
                        <div className="flex items-center gap-2">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm font-semibold">{prof.overall_rating.toFixed(1)}/5.0</span>
                          {prof.total_ratings && (
                            <span className="text-sm text-muted-foreground">({prof.total_ratings} évaluations)</span>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <p className="text-xs text-gray-500 mt-4">
              Données provenant de RateMyProfessor.com
            </p>
          </div>
        )}

        {/* Course Details */}
        {(blogPost.prerequisites || blogPost.required_in_programs || blogPost.outline) && (
          <div className="bg-card rounded-2xl shadow-sm border border-border p-6 mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-4">Informations sur le cours</h2>
            <div className="space-y-4">
              {blogPost.prerequisites && (
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Prérequis</h3>
                  <p className="text-foreground/90">{blogPost.prerequisites}</p>
                </div>
              )}
              {blogPost.required_in_programs && blogPost.required_in_programs.length > 0 && (
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Programmes nécessitant ce cours</h3>
                  <ul className="list-disc list-inside text-foreground/90 space-y-1">
                    {blogPost.required_in_programs.map((program, index) => (
                      <li key={index}>{program}</li>
                    ))}
                  </ul>
                </div>
              )}
              {blogPost.outline && (
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Plan de cours</h3>
                  <div className="text-foreground/90 prose max-w-none">
                    <ReactMarkdown>{blogPost.outline}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="bg-card rounded-2xl shadow-sm border border-border p-8 mb-8">
          <div className="prose prose-lg max-w-none prose-headings:text-foreground prose-headings:font-bold prose-h2:text-2xl prose-h2:mt-8 prose-h2:mb-4 prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3 prose-p:text-foreground/90 prose-p:mb-4 prose-p:leading-relaxed prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-strong:text-foreground prose-ul:text-foreground/90 prose-ol:text-foreground/90 prose-li:my-2">
            {(() => {
              // Remove CTA button HTML and professor ratings section from content
              let cleanedContent = blogPost.content;
              
              // Remove CTA button (more robust regex to handle newlines)
              const ctaRegex = /<div\s+class=["']cta-section["'][\s\S]*?<\/div>/gi;
              cleanedContent = cleanedContent.replace(ctaRegex, '').trim();
              
              // Remove professor ratings section (from "## Évaluations des professeurs" to next heading or end)
              const ratingsRegex = /##\s+Évaluations des professeurs[\s\S]*?(?=##\s+|$)/i;
              cleanedContent = cleanedContent.replace(ratingsRegex, '').trim();
              
              // Clean up any double blank lines
              cleanedContent = cleanedContent.replace(/\n{3,}/g, '\n\n');
              
              return <ReactMarkdown>{cleanedContent}</ReactMarkdown>;
            })()}
          </div>
        </div>

        {/* FAQ Section */}
        {blogPost.faq_content && (
          <div className="bg-card rounded-2xl shadow-sm border border-border p-8 mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-6">Questions fréquemment posées</h2>
            <div className="prose prose-lg max-w-none">
              <ReactMarkdown>{blogPost.faq_content}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* CTA Section - Bottom */}
        {isActive ? (
          <div className="bg-primary rounded-2xl shadow-lg p-8 text-center text-primary-foreground">
            <h2 className="text-3xl font-bold mb-4">Prêt à réussir ce cours ?</h2>
            <p className="text-lg mb-6 opacity-90">
              Réservez une séance de tutorat avec un de nos tuteurs qualifiés
            </p>
            <a
              href={reservationUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-card text-primary hover:bg-muted font-semibold py-4 px-8 rounded-xl text-lg transition-colors"
            >
              Réserver maintenant
              <ArrowRight className="h-5 w-5" />
            </a>
          </div>
        ) : (
          <div className="bg-primary rounded-2xl shadow-lg p-8 text-center text-primary-foreground">
            <h2 className="text-3xl font-bold mb-4">Prêt à réussir ce cours ?</h2>
            <p className="text-lg mb-6 opacity-90">
              Commencez par remplir notre questionnaire pour trouver le tuteur idéal
            </p>
            <a
              href={questionnaireUrl}
              className="inline-flex items-center gap-2 bg-card text-primary hover:bg-muted font-semibold py-4 px-8 rounded-xl text-lg transition-colors"
            >
              Commencer le questionnaire
              <ArrowRight className="h-5 w-5" />
            </a>
          </div>
        )}
          </div>

          {/* Sidebar with related content - Aligned with content box */}
          <RelatedContentSidebar
            type="course"
            courseSlug={blogPost.course_slug}
            domain={course?.domain}
            institution={course?.institution}
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

