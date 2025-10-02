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

export type Step = 'course' | 'helpType' | 'when' | 'name' | 'email' | 'thank-you';