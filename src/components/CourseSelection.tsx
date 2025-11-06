import React, { useState, useEffect, useRef } from 'react';
import { Search } from 'lucide-react';
import { searchCourses } from '../lib/supabase';
import { Course } from '../types';

interface CourseSelectionProps {
  onSelect: (course: { code: string; slug: string; displayText: string }) => void;
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
      displayText: courseText
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedCourse) {
      onNext();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header with Logo */}
      <div className="absolute top-3 left-3 sm:top-4 sm:left-4 z-10">
        <img 
          src="/dark_logo.png" 
          alt="Carré d'As Tutorat" 
          className="h-10 sm:h-12 w-auto"
        />
      </div>

      {/* Tutor Application Button */}
      <div className="absolute top-3 right-3 sm:top-4 sm:right-4 z-10">
        <a
          href="/devenez-tuteur"
          className="inline-block bg-white/80 hover:bg-white text-gray-700 hover:text-gray-900 font-medium py-2 px-4 rounded-lg text-sm transition-all duration-200 shadow-sm hover:shadow-md border border-gray-200"
        >
          DEVENEZ TUTEUR
        </a>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4 pt-20">
        <div className="max-w-2xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-8 leading-tight">
            J'ai besoin d'aide pour mon cours de...
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="relative">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-6 w-6 text-gray-400" />
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
              className="w-full pl-12 pr-4 py-6 text-xl border-2 border-gray-200 rounded-2xl focus:border-[#00746b] focus:outline-none transition-colors"
              autoComplete="off"
            />
          </div>

          {showDropdown && (
            <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
              {loading ? (
                <div className="p-4 text-center text-gray-500">Recherche en cours...</div>
              ) : courses.length > 0 ? (
                courses.map((course) => (
                  <button
                    key={course.id}
                    type="button"
                    onClick={() => handleCourseSelect(course)}
                    className="w-full text-left p-4 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
                  >
                    <div className="font-medium text-gray-900">{course.title_fr}</div>
                    {(course.code || course.institution) && (
                      <div className="text-sm text-gray-500">
                        {course.code && course.institution 
                          ? `${course.code} (${course.institution})`
                          : course.code || course.institution
                        }
                      </div>
                    )}
                  </button>
                ))
              ) : (
                <div className="p-4 text-center text-gray-500">Aucun cours trouvé</div>
              )}
            </div>
          )}

          <div className="mt-8 text-center">
            <button
              type="submit"
              disabled={!selectedCourse}
              className="bg-[#00746b] hover:bg-[#005a52] disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-4 px-12 rounded-xl text-lg transition-colors"
            >
              Continuer
            </button>
          </div>
        </form>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-4 text-gray-500 text-sm">
        © 2025 Carré d'As Tutorat. Tous droits réservés.
      </div>
    </div>
  );
}