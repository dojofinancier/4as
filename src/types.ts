export interface Course {
  id: string;
  full_name: string;
  code?: string;
  institution?: string;
  created_at: string;
}

export interface FormData {
  course: string;
  helpTypes: string[];
  whenNeeded: string;
  name: string;
  email: string;
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