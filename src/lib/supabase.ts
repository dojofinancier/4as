import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabasePublishableKey) {
  throw new Error('Missing Supabase environment variables. Please check your .env file.');
}

export const supabase = createClient(supabaseUrl, supabasePublishableKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false
  }
});

export async function searchCourses(query: string) {
  if (!query.trim()) return [];
  
  const { data, error } = await supabase
    .from('courses')
    .select('*')
    .or(`full_name.ilike.%${query}%,code.ilike.%${query}%`)
    .limit(10);
    
  if (error) {
    console.error('Error searching courses:', error);
    return [];
  }
  
  return data || [];
}