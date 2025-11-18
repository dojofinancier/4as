import { useNavigate } from 'react-router-dom';
import { Home, BookOpen } from 'lucide-react';

export function BlogPostNotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">
        <BookOpen className="h-24 w-24 text-muted-foreground/70 mx-auto mb-6" />
        <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
          Article non trouvé
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          L'article de blog que vous recherchez n'existe pas ou n'est plus disponible.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate('/')}
            className="inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-8 rounded-xl transition-colors"
          >
            <Home className="h-5 w-5" />
            Retour à l'accueil
          </button>
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center justify-center gap-2 bg-card hover:bg-background text-foreground/90 font-semibold py-3 px-8 rounded-xl transition-colors border border-border"
          >
            Retour en arrière
          </button>
        </div>
      </div>
    </div>
  );
}

