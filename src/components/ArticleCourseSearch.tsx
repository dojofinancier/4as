import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { searchCourses } from '../lib/supabase';
import { Course } from '../types';

interface ArticleCourseSearchProps {
  onCourseSelect?: (course: { code: string; slug: string; displayText: string; title: string; active?: boolean }) => void;
}

export function ArticleCourseSearch({ onCourseSelect }: ArticleCourseSearchProps) {
  const navigate = useNavigate();
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
    
    // Prepare course data
    const courseData = {
      code: course.code,
      slug: course.slug,
      displayText: courseText,
      title: course.title_fr,
      active: course.active
    };
    
    // Call optional callback
    if (onCourseSelect) {
      onCourseSelect(courseData);
    }
    
    // Navigate to questionnaire with course pre-selected
    navigate('/', { 
      state: { 
        selectedCourse: courseData 
      } 
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedCourse) {
      // Find the course in the current results
      const course = courses.find(c => {
        const courseText = c.code && c.institution 
          ? `${c.title_fr} (${c.code} - ${c.institution})`
          : c.code 
          ? `${c.title_fr} (${c.code})`
          : c.title_fr;
        return courseText === selectedCourse;
      });
      
      if (course) {
        handleCourseSelect(course);
      }
    }
  };

  return (
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
          className="w-full pl-12 pr-4 py-6 text-xl text-foreground bg-card border-2 border-border rounded-2xl focus:border-primary focus:outline-none transition-colors placeholder:text-muted-foreground/70"
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
    </form>
  );
}

