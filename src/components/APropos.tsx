import { Footer } from './Footer';
import { User } from 'lucide-react';

export function APropos() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header with Logo */}
      <div className="absolute top-3 left-3 sm:top-4 sm:left-4 z-10">
        <a href="/">
          <img 
            src="/dark_logo_high.png" 
            alt="Carré d'As Tutorat" 
            className="h-10 sm:h-12 w-auto"
          />
        </a>
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

      <div className="container mx-auto px-4 py-12 pt-20 max-w-4xl">
        <article className="prose prose-lg max-w-none">
          <h1 className="text-4xl font-bold text-foreground mb-8">À propos</h1>
          
          <h2 className="text-2xl font-bold text-foreground mt-8 mb-4">NOTRE MISSION</h2>
          <p className="text-foreground mb-4">
            Chez Carré d'As, notre mission est simple: donner aux étudiants présents à nos cours intensifs tous les outils nécessaires pour qu'ils dépassent leurs propres objectifs académiques. Notre but est de mettre toutes les chances du côté des étudiants et de les préparer adéquatement aux examens. À cette fin, nous recherchons constamment les instructeurs les plus compétents et nous offrons un cours seulement après nous être assuré qu'il correspond à nos exigences de qualité.
          </p>
          <p className="text-foreground mb-4">
            Nos tuteurs sont tous d'anciens étudiants ayant de l'expérience de tutorat ou d'enseignement et ayant obtenu un diplôme de deuxième cycle et/ou une désignation professionnelle dans leur domaine. Nous travaillons avec des tuteurs possédant de l'expérience de travail dans la matière enseignée afin qu'ils puissent transmettre aux étudiants une perspective réaliste du matériel couvert plutôt que seulement réciter la théorie.
          </p>

          <h2 className="text-2xl font-bold text-foreground mt-8 mb-4">LA GARANTIE CARRÉ D'AS TUTORAT</h2>
          <p className="text-foreground mb-4">
            Depuis nos débuts, nous sommes fiers d'avoir toujours été à l'écoute de notre clientèle et d'assurer un service professionnel et de grande qualité. La garantie Carré d'As Tutorat s'énumère en quatre volets.
          </p>
          <p className="text-foreground mb-4">
            <strong>Communication.</strong> Nous continuons de nous assurer de maintenir une bonne communication avec les clients, étudiants et tuteurs afin d'être à l'écoute des suggestions et commentaires. Toute notre communication est faite de façon personnalisée et nous répondons à tous les courriels.
          </p>
          <p className="text-foreground mb-4">
            <strong>Tuteurs compétents et pédagogiques.</strong> Nous nous efforçons à dénicher des tuteurs non seulement compétents mais possédant aussi les bonnes capacités pédagogiques afin d'enseigner la matière de manière fluide et claire. Nous sommes très sévères sur la performance de nos tuteurs et nous n'avons jamais hésité à remplacer un tuteur qui ne correspondait pas à nos critères de qualité.
          </p>
          <p className="text-foreground mb-4">
            <strong>Service Adapté.</strong> Carré d'As Tutorat s'engage à aider tous les étudiants dans les cours offerts peu importe leur niveau. Même si vous n'avez rien compris à la matière ou que vous n'avez pas encore commencé à étudier, nous pouvons vous offrir une solution adaptée.
          </p>
          <p className="text-foreground mb-4">
            <strong>Sécurité et confidentialité.</strong> Notre site web est entièrement encrypté et nous ne collectons aucune information sur votre carte de crédit. Aussi, Carré d'As Tutorat ne partage aucune des informations des clients à de tierce partie. De plus vous pouvez effectuer votre inscription en confiance car vous serez remboursé si vous annulez au moins 2 jours avant le cours.
          </p>

          <h2 className="text-2xl font-bold text-foreground mt-8 mb-4">Pourquoi le tutorat?</h2>
          <p className="text-foreground mb-4">
            Carré d'As Tutorat offre depuis plusieurs années des séances de tutorat privé. Le format du tutorat privé est beaucoup plus flexible que les cours intensifs et sont à la discretion de l'étudiant et du tuteur.
          </p>
          <p className="text-foreground mb-4">
            Il existe plusieurs raisons pour lesquelles un étudiant fasse appel au tutorat privé. Par exemple:
          </p>
          <ul className="list-disc pl-6 mb-4 text-foreground">
            <li>L'étudiant peut avoir pris du retard sur le matériel assigné et à besoin de rattrapage</li>
            <li>L'étudiant à de la difficulté à faire ses études individuellement (manque de motivation, concentration, temps,…)</li>
            <li>L'étudiant n'arrive pas à comprendre les explications de l'enseignant</li>
            <li>Certains exercices assignés nécessitent des explications supplémentaires</li>
            <li>L'enseignant est peu/pas disponible pour des explications supplémentaires</li>
          </ul>
        </article>
      </div>
      <Footer />
    </div>
  );
}

