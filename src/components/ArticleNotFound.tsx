import { useNavigate } from 'react-router-dom';

export function ArticleNotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-3xl font-bold text-foreground mb-4">Article non trouvé</h1>
        <p className="text-muted-foreground mb-8">
          L'article que vous recherchez n'existe pas ou n'est plus disponible.
        </p>
        <button
          onClick={() => navigate('/')}
          className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-8 rounded-xl transition-colors"
        >
          Retour à l'accueil
        </button>
      </div>
    </div>
  );
}

