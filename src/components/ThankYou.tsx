import { CheckCircle } from 'lucide-react';
import { Footer } from './Footer';

interface ThankYouProps {
  courseName?: string;
  onBackToSearch?: () => void;
}

export function ThankYou({ courseName, onBackToSearch }: ThankYouProps) {
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

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4 pt-20">
        <div className="max-w-2xl w-full text-center">
        <CheckCircle className="h-24 w-24 text-primary mx-auto mb-8" />
        
        <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
          Merci !
        </h1>
        
        <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
          Nous avons bien reçu votre demande d'aide pour le cours de {courseName || 'ce cours'}.
          <br />
          <br />
          Malheureusement, pour le moment nous n'avons pas de tuteur de <strong>{courseName || 'ce cours'}</strong> disponible.
          <br />
          <br />
          Nous sommes présentement à la recherche d'un tuteur qualifié pour ce cours et nous vous contacterons dès que nous en trouverons un.
        </p>
        
        <div className="bg-card p-8 rounded-2xl shadow-sm border border-border">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Que se passe-t-il maintenant ?
          </h3>
          <ul className="text-left text-muted-foreground space-y-3">
            <li className="flex items-start">
              <span className="text-primary mr-3">1.</span>
              Nous recherchons un tuteur qualifié pour votre cours
            </li>
            <li className="flex items-start">
              <span className="text-primary mr-3">2.</span>
              Vous recevrez un email dès qu'un tuteur sera disponible
            </li>
          </ul>
        </div>

        {onBackToSearch && (
          <div className="mt-8">
            <button
              onClick={onBackToSearch}
              className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-4 px-12 rounded-xl text-lg transition-colors"
            >
              Chercher un autre cours
            </button>
          </div>
        )}
        </div>
      </div>

      <Footer />
    </div>
  );
}