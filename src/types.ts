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

export type Step = 'course' | 'helpType' | 'when' | 'name' | 'email' | 'thank-you' | 'unavailable';