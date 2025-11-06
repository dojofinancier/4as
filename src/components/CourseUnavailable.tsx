import { AlertCircle } from 'lucide-react';

interface CourseUnavailableProps {
  courseCode: string;
  onBackToSearch: () => void;
}

export function CourseUnavailable({ courseCode, onBackToSearch }: CourseUnavailableProps) {
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

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4 pt-20">
        <div className="max-w-2xl w-full text-center">
        <AlertCircle className="h-24 w-24 text-[#00746b] mx-auto mb-8" />
        
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Aucun tuteur disponible
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 leading-relaxed">
          Désolé, il n'y a actuellement aucun tuteur disponible pour ce cours.
          <br />
          <span className="text-lg text-gray-500 mt-2 block">
            (Code du cours: {courseCode})
          </span>
        </p>
        
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Que pouvez-vous faire ?
          </h3>
          <ul className="text-left text-gray-600 space-y-3">
            <li className="flex items-start">
              <span className="text-[#00746b] mr-3">•</span>
              Recherchez un autre cours qui pourrait vous aider
            </li>
            <li className="flex items-start">
              <span className="text-[#00746b] mr-3">•</span>
              Vérifiez à nouveau plus tard - de nouveaux tuteurs peuvent s'ajouter
            </li>
            <li className="flex items-start">
              <span className="text-[#00746b] mr-3">•</span>
              Contactez-nous si vous avez des questions spécifiques
            </li>
          </ul>
        </div>

        <button
          onClick={onBackToSearch}
          className="bg-[#00746b] hover:bg-[#005a52] text-white font-semibold py-4 px-12 rounded-xl text-lg transition-colors"
        >
          Rechercher un autre cours
        </button>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-4 text-gray-500 text-sm">
        © 2025 Carré d'As Tutorat. Tous droits réservés.
      </div>
    </div>
  );
}



