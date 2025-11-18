import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Search, BookOpen, FileText, Calendar, Tag } from 'lucide-react';
import { Helmet } from 'react-helmet-async';
import { searchBlogPosts, searchGeneralArticles, getAllDomains, getAllArticleCategories } from '../lib/supabase';
import { CourseBlogPost, GeneralArticle } from '../types';
import { Footer } from './Footer';
import { User } from 'lucide-react';

interface BlogListingItem {
  id: string;
  type: 'blog' | 'article';
  title: string;
  excerpt?: string | null;
  slug: string;
  published_at?: string | null;
  category?: string;
  domain?: string;
  tags?: string[];
  keywords?: string[];
}

export function BlogListing() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [contentType, setContentType] = useState<'all' | 'blogs' | 'articles'>('all');

  // Fetch domains and categories
  const { data: domains = [] } = useQuery({
    queryKey: ['domains'],
    queryFn: getAllDomains,
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['articleCategories'],
    queryFn: getAllArticleCategories,
  });

  // Fetch blogs
  const { data: blogs = [], isLoading: blogsLoading } = useQuery({
    queryKey: ['blogPosts', searchQuery, selectedCategory === 'all' ? undefined : selectedCategory],
    queryFn: () => searchBlogPosts(
      searchQuery,
      selectedCategory !== 'all' && domains.includes(selectedCategory) ? selectedCategory : undefined,
      200
    ),
  });

  // Fetch articles
  const { data: articles = [], isLoading: articlesLoading } = useQuery({
    queryKey: ['generalArticles', searchQuery, selectedCategory === 'all' ? undefined : selectedCategory],
    queryFn: () => searchGeneralArticles(
      searchQuery,
      selectedCategory !== 'all' && categories.includes(selectedCategory) ? selectedCategory : undefined,
      200
    ),
  });

  // Combine and filter items
  const items = useMemo(() => {
    console.log(`[BlogListing] Processing ${blogs.length} blogs and ${articles.length} articles`);
    
    const blogItems: BlogListingItem[] = blogs.map((blog: CourseBlogPost) => ({
      id: blog.id,
      type: 'blog' as const,
      title: blog.title,
      excerpt: blog.excerpt,
      slug: blog.blog_slug || blog.course_slug,
      published_at: blog.published_at,
      domain: undefined, // Will be fetched separately if needed
    }));

    const articleItems: BlogListingItem[] = articles.map((article: GeneralArticle) => ({
      id: article.id,
      type: 'article' as const,
      title: article.title,
      excerpt: article.excerpt,
      slug: article.slug,
      published_at: article.published_at,
      category: article.category,
      tags: article.tags,
      keywords: article.keywords,
    }));

    let combined: BlogListingItem[] = [];

    if (contentType === 'all') {
      combined = [...blogItems, ...articleItems];
    } else if (contentType === 'blogs') {
      combined = blogItems;
    } else {
      combined = articleItems;
    }

    // Sort by published_at (most recent first)
    combined.sort((a, b) => {
      const dateA = a.published_at ? new Date(a.published_at).getTime() : 0;
      const dateB = b.published_at ? new Date(b.published_at).getTime() : 0;
      return dateB - dateA;
    });

    return combined;
  }, [blogs, articles, contentType]);

  const isLoading = blogsLoading || articlesLoading;

  // Get all available categories (domains + article categories)
  const allCategories = useMemo(() => {
    return ['all', ...domains, ...categories];
  }, [domains, categories]);

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-CA', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  return (
    <div className="min-h-screen bg-background">
      <Helmet>
        <title>Blog et Articles | Carré d'As Tutorat</title>
        <meta name="description" content="Découvrez nos articles et guides sur les cours, le tutorat et les études universitaires." />
      </Helmet>

      {/* Header with Logo */}
      <div className="absolute top-3 left-3 sm:top-4 sm:left-4 z-10">
        <a href="/">
          <img 
            src="/dark_logo_high.png" 
            alt="Carré d'As Tutorat" 
            className="h-10 sm:h-12 w-auto"
          />
        </a>
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
      <div className="container mx-auto px-4 py-12 pt-20 max-w-6xl">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-4">Blog et Articles</h1>
          <p className="text-muted-foreground text-lg">
            Découvrez nos guides, conseils et ressources pour réussir vos cours
          </p>
        </header>

        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Rechercher par titre, mots-clés ou tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-border rounded-xl focus:border-primary focus:outline-none bg-background text-foreground"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4">
            {/* Content Type Filter */}
            <div className="flex gap-2">
              <button
                onClick={() => setContentType('all')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  contentType === 'all'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card text-foreground hover:bg-muted border border-border'
                }`}
              >
                Tout
              </button>
              <button
                onClick={() => setContentType('blogs')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  contentType === 'blogs'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card text-foreground hover:bg-muted border border-border'
                }`}
              >
                <BookOpen className="h-4 w-4" />
                Cours
              </button>
              <button
                onClick={() => setContentType('articles')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  contentType === 'articles'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card text-foreground hover:bg-muted border border-border'
                }`}
              >
                <FileText className="h-4 w-4" />
                Articles
              </button>
            </div>

            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 rounded-lg bg-card text-foreground border border-border focus:border-primary focus:outline-none"
            >
              <option value="all">Toutes les catégories</option>
              {domains.map((domain) => (
                <option key={domain} value={domain}>
                  {domain}
                </option>
              ))}
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Chargement...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">
              {searchQuery ? 'Aucun résultat trouvé pour votre recherche.' : 'Aucun contenu disponible.'}
            </p>
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-muted-foreground">
              {items.length} {items.length === 1 ? 'résultat' : 'résultats'} trouvé{items.length > 1 ? 's' : ''}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {items.map((item) => (
                <Link
                  key={item.id}
                  to={item.type === 'blog' ? `/${item.slug}` : `/article/${item.slug}`}
                  className="block bg-card rounded-xl border border-border p-6 hover:border-primary transition-all hover:shadow-lg group"
                >
                  <div className="flex items-start gap-3 mb-3">
                    {item.type === 'blog' ? (
                      <BookOpen className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
                    ) : (
                      <FileText className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
                    )}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-2 mb-2">
                        {item.title}
                      </h3>
                      {item.excerpt && (
                        <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
                          {item.excerpt}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <div className="flex items-center gap-2">
                      {item.published_at && (
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(item.published_at)}</span>
                        </div>
                      )}
                    </div>
                    {item.category && (
                      <div className="flex items-center gap-1">
                        <Tag className="h-3 w-3" />
                        <span>{item.category}</span>
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </>
        )}
      </div>

      <Footer />
    </div>
  );
}

