import React, { useState, useEffect, useRef } from 'react';
import { Search, User } from 'lucide-react';
import { searchCourses } from '../lib/supabase';
import { Course } from '../types';
import { Footer } from './Footer';

interface CourseSelectionProps {
  onSelect: (course: { code: string; slug: string; displayText: string; title: string; active?: boolean }) => void;
  onNext: () => void;
}

export function CourseSelection({ onSelect, onNext }: CourseSelectionProps) {
  const [query, setQuery] = useState('');
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const searchDebounced = setTimeout(async () => {
      if (query.length > 1 && !selectedCourse) {
        setLoading(true);
        const results = await searchCourses(query);
        setCourses(results);
        setShowDropdown(true);
        setLoading(false);
      } else if (!selectedCourse) {
        setCourses([]);
        setShowDropdown(false);
      }
    }, 300);

    return () => clearTimeout(searchDebounced);
  }, [query, selectedCourse]);

  const handleCourseSelect = (course: Course) => {
    // Create display text for the input field
    let courseText = course.title_fr;
    if (course.code && course.institution) {
      courseText = `${course.title_fr} (${course.code} - ${course.institution})`;
    } else if (course.code) {
      courseText = `${course.title_fr} (${course.code})`;
    }
    
    setSelectedCourse(courseText);
    setQuery(courseText);
    setShowDropdown(false);
    setCourses([]);
    
    // Pass course data as object for availability check and redirect
    onSelect({
      code: course.code,
      slug: course.slug,
      displayText: courseText,
      title: course.title_fr,
      active: course.active
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedCourse) {
      onNext();
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header with Logo */}
      <div className="absolute top-3 left-3 sm:top-4 sm:left-4 z-10">
        <img 
          src="/dark_logo_high.png" 
          alt="Carré d'As Tutorat" 
          className="h-10 sm:h-12 w-auto"
        />
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
      <div className="flex-1 flex items-center justify-center p-4 pt-20">
        <div className="max-w-2xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-8 leading-tight">
            J'ai besoin d'aide pour mon cours de...
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="relative">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-6 w-6 text-muted-foreground/70" />
            </div>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (selectedCourse) {
                  setSelectedCourse('');
                  setShowDropdown(false);
                  setCourses([]);
                }
              }}
              placeholder="Tapez le nom de votre cours..."
              className="w-full pl-12 pr-4 py-6 text-xl border-2 border-border rounded-2xl focus:border-primary focus:outline-none transition-colors"
              autoComplete="off"
            />
          </div>

          {showDropdown && (
            <div className="absolute z-10 w-full mt-2 bg-card border border-border rounded-xl shadow-lg max-h-60 overflow-y-auto">
              {loading ? (
                <div className="p-4 text-center text-muted-foreground">Recherche en cours...</div>
              ) : courses.length > 0 ? (
                courses.map((course) => (
                  <button
                    key={course.id}
                    type="button"
                    onClick={() => handleCourseSelect(course)}
                    className="w-full text-left p-4 hover:bg-muted border-b border-border/50 last:border-b-0 transition-colors"
                  >
                    <div className="font-medium text-foreground">{course.title_fr}</div>
                    {(course.code || course.institution) && (
                      <div className="text-sm text-muted-foreground">
                        {course.code && course.institution 
                          ? `${course.code} (${course.institution})`
                          : course.code || course.institution
                        }
                      </div>
                    )}
                  </button>
                ))
              ) : (
                <div className="p-4 text-center text-muted-foreground">Aucun cours trouvé</div>
              )}
            </div>
          )}

          <div className="mt-8 text-center">
            <button
              type="submit"
              disabled={!selectedCourse}
              className="bg-primary hover:bg-primary/90 disabled:bg-muted disabled:cursor-not-allowed text-primary-foreground font-semibold py-4 px-12 rounded-xl text-lg transition-colors border-2 border-primary disabled:border-muted"
            >
              Continuer
            </button>
          </div>
        </form>
        </div>
      </div>

      <Footer />
    </div>
  );
}