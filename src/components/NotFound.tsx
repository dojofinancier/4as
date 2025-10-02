import { Home, ArrowLeft } from 'lucide-react';

export function NotFound() {
  const goBack = () => {
    window.history.back();
  };

  const goHome = () => {
    window.location.href = '/';
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

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4 pt-20">
        <div className="max-w-2xl w-full text-center">
          {/* 404 Icon */}
          <div className="text-8xl md:text-9xl font-bold text-gray-300 mb-8">
            404
          </div>
          
          {/* Error Message */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Page non trouvée
          </h1>
          
          <p className="text-lg text-gray-600 mb-8">
            Désolé, la page que vous recherchez n'existe pas ou a été déplacée.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={goBack}
              className="flex items-center justify-center gap-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-xl transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              Retour
            </button>
            
            <button
              onClick={goHome}
              className="flex items-center justify-center gap-2 bg-[#00746b] hover:bg-[#005a52] text-white font-semibold py-3 px-6 rounded-xl transition-colors"
            >
              <Home className="h-5 w-5" />
              Accueil
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-4 text-gray-500 text-sm">
        © 2025 Carré d'As Tutorat. Tous droits réservés.
      </div>
    </div>
  );
}
