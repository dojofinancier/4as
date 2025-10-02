import { CheckCircle } from 'lucide-react';

export function ThankYou() {
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
        <CheckCircle className="h-24 w-24 text-[#00746b] mx-auto mb-8" />
        
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          Merci !
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 leading-relaxed">
          Votre demande d'aide a été envoyée avec succès. 
          <br />
          Nous vous contacterons très bientôt pour vous mettre en relation avec un tuteur qualifié.
        </p>
        
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Que se passe-t-il maintenant ?
          </h3>
          <ul className="text-left text-gray-600 space-y-3">
            <li className="flex items-start">
              <span className="text-[#00746b] mr-3">1.</span>
              Notre équipe analyse votre demande
            </li>
            <li className="flex items-start">
              <span className="text-[#00746b] mr-3">2.</span>
              Nous sélectionnons le tuteur le mieux adapté
            </li>
            <li className="flex items-start">
              <span className="text-[#00746b] mr-3">3.</span>
              Vous recevez un email avec les détails de contact
            </li>
          </ul>
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