import { CheckCircle } from 'lucide-react';
import { Footer } from './Footer';

export function TutorThankYou() {
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
            Merci pour votre candidature !
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
            Votre candidature pour devenir tuteur a été reçue avec succès.
            <br />
            Nous examinerons votre profil et nous vous contacterons si vous êtes sélectionné pour une entrevue.
          </p>
          
          <div className="bg-card p-8 rounded-2xl shadow-sm border border-border">
            <h3 className="text-lg font-semibold text-foreground mb-4">
              Prochaines étapes
            </h3>
            <ul className="text-left text-muted-foreground space-y-3">
              <li className="flex items-start">
                <span className="text-primary mr-3">1.</span>
                Notre équipe examine votre candidature et votre CV
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-3">2.</span>
                Si votre profil correspond à nos besoins, nous vous contacterons
              </li>
              <li className="flex items-start">
                <span className="text-primary mr-3">3.</span>
                Nous planifierons une entrevue pour mieux vous connaître
              </li>
            </ul>
          </div>

          <div className="mt-8">
            <a
              href="/"
              className="inline-block bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-8 rounded-xl text-lg transition-colors"
            >
              Retour à l'accueil
            </a>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
