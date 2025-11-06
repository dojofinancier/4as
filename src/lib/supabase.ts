import { createClient } from '@supabase/supabase-js';
import { CourseAvailability } from '../types';

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
    .eq('active', true)
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