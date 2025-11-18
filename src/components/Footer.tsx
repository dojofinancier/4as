import { Link } from 'react-router-dom';

export function Footer() {
  return (
    <footer className="text-center py-6 text-muted-foreground text-sm border-t border-border mt-12">
      <div className="container mx-auto px-4">
        <p className="mb-2">© 2025 Carré d'As Tutorat. Tous droits réservés.</p>
        <div className="flex flex-wrap justify-center gap-4 text-xs text-muted-foreground/70">
          <Link 
            to="/a-propos" 
            className="hover:text-muted-foreground transition-colors"
          >
            À propos
          </Link>
          <span className="text-muted-foreground/30">•</span>
          <Link 
            to="/blog" 
            className="hover:text-muted-foreground transition-colors"
          >
            Blog
          </Link>
          <span className="text-muted-foreground/30">•</span>
          <Link 
            to="/politique-de-confidentialite" 
            className="hover:text-muted-foreground transition-colors"
          >
            Politique de confidentialité
          </Link>
          <span className="text-muted-foreground/30">•</span>
          <Link 
            to="/termes-et-conditions" 
            className="hover:text-muted-foreground transition-colors"
          >
            Termes et conditions
          </Link>
        </div>
      </div>
    </footer>
  );
}

