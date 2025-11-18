export interface Course {
  id: string;
  title_fr: string;
  code: string;
  slug: string;
  institution?: string;
  active?: boolean;
  created_at: string;
}

export interface FormData {
  course: string; // For webhook (full text display)
  courseCode: string; // For availability check
  courseSlug: string | null; // For redirect
  courseDisplayText: string; // For display/webhook
  courseTitle: string; // Course title only (without code/institution)
  courseActive?: boolean; // Whether the course is active
  helpTypes: string[];
  whenNeeded: string;
  name: string;
  email: string;
}

export interface CourseAvailability {
  available: boolean;
  slug: string | null;
  tutorsCount: number;
}

export interface TutorApplicationData {
  prenom: string;
  nom: string;
  email: string;
  telephone: string;
  domaineEtude: string[];
  autreDomaine?: string;
  niveauEtude: string;
  disponibilites: string[];
  experienceTutorat: string;
  cvFile?: File;
  cvUrl?: string;
}

export type Step = 'course' | 'helpType' | 'when' | 'name' | 'email' | 'thank-you';

// Blog Post Types
export interface CourseBlogPost {
  id: string;
  course_slug: string;
  blog_slug?: string | null; // SEO-friendly slug for URL (e.g., "analyse-des-valeurs-mobilieres-1")
  course_code: string;
  title: string;
  h1?: string | null;
  content: string;
  excerpt?: string | null;
  meta_description?: string | null;
  faq_content?: string | null;
  json_ld?: Record<string, any> | null;
  canonical_url?: string | null;
  og_image_url?: string | null;
  word_count?: number | null;
  similarity_score?: number | null;
  is_indexable?: boolean | null;
  published: boolean;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
  author?: string | null;
  featured_image_url?: string | null;
  // Course customization fields
  outline?: string | null;
  website_description?: string | null;
  prerequisites?: string | null;
  required_in_programs?: string[] | null;
}

// Professor Rating Types
export interface ProfessorRating {
  id: string;
  course_slug: string;
  professor_name: string;
  professor_rmp_id?: string | null;
  overall_rating?: number | null;
  difficulty_rating?: number | null;
  would_take_again?: number | null;
  total_ratings?: number | null;
  best_for?: string | null;
  worst_for?: string | null;
  last_updated?: string | null;
  created_at: string;
  updated_at: string;
}

// Helper types for blog post operations
export type CourseBlogPostCreate = Omit<CourseBlogPost, 'id' | 'created_at' | 'updated_at'>;
export type CourseBlogPostUpdate = Partial<Omit<CourseBlogPost, 'id' | 'course_slug' | 'created_at'>>;

// Blog post with related course data
export interface CourseBlogPostWithCourse extends CourseBlogPost {
  course?: Course;
  professor_ratings?: ProfessorRating[];
}

// General Article Types
export interface InternalLink {
  slug: string;
  anchor_text: string;
  position: number;
}

export interface ExternalLink {
  url: string;
  anchor_text: string;
  description: string;
  position: number;
}

export interface GeneralArticle {
  id: string;
  slug: string;
  title: string;
  category: string;
  tags: string[];
  keywords: string[];
  draft_outline?: string | null;
  content?: string | null;
  excerpt?: string | null;
  meta_description?: string | null;
  h1?: string | null;
  internal_links: InternalLink[];
  related_articles: string[];
  external_links: ExternalLink[];
  word_count?: number | null;
  similarity_score?: number | null;
  is_indexable: boolean;
  status: 'draft_outline' | 'draft' | 'published';
  published: boolean;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
  author?: string | null;
  featured_image_url?: string | null;
  json_ld?: Record<string, any> | null;
}

export type GeneralArticleCreate = Omit<GeneralArticle, 'id' | 'created_at' | 'updated_at'>;
export type GeneralArticleUpdate = Partial<Omit<GeneralArticle, 'id' | 'slug' | 'created_at'>>;