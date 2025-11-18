import { Footer } from './Footer';
import { User } from 'lucide-react';

export function PolitiqueConfidentialite() {
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
          <h1 className="text-4xl font-bold text-foreground mb-8">Politique de confidentialité</h1>
          
          <p className="text-foreground mb-4">
            Carré d'As Tutorat accorde une grande importance à vos renseignements personnels. Nous nous sommes engagés à protéger les renseignements personnels des visiteurs de notre site Web. Les politiques régissant la protection de la vie privée sont strictement observées de façon à satisfaire aux normes les plus élevées en la matière. Les faits saillants concernant la politique de confidentialité préconisée par Carré d'As Tutorat relativement à la collecte des renseignements sont présentés comme suit :
          </p>

          <p className="text-foreground mb-4">
            Nous recueillons les renseignements personnels uniquement pour vous identifier lorsque vous visitez de nouveau le site Web ou pour vous faciliter nos services. Nous ne communiquons, ni ne vendons en aucun cas vos renseignements personnels à des tiers;
          </p>

          <p className="text-foreground mb-4">
            Carré d'As Tutorat peut utiliser tout renseignement recueilli pour fournir un meilleur service à la clientèle, améliorer son site Web, répondre à vos besoins particuliers, fournir de futurs envois de renseignements d'intérêt et aux fins de marketing. Les renseignements peuvent également être utilisés pour fournir un registre des communications entre vous et Carré d'As Tutorat et pour se conformer à toute exigence juridique et/ou règlementaire;
          </p>

          <p className="text-foreground mb-4">
            Les renseignements personnels recueillis par Carré d'As Tutorat peuvent servir à déterminer le nombre de personnes qui accèdent au site Web ainsi que les sections du site Web qui sont les plus consultées. Lorsque vous accédez au site Web, vous vous déplacez de page en page, vous lisez des pages ou vous téléchargez le contenu à votre ordinateur, les renseignements suivants peuvent être retenus :
          </p>

          <ul className="list-disc pl-6 mb-4 text-foreground">
            <li>L'adresse IP à partir de laquelle vous vous connectez;</li>
            <li>Les pages consultées;</li>
            <li>Le contenu téléchargé;</li>
            <li>L'adresse des sites Web que vous avez visités immédiatement avant d'accéder à notre site Web.</li>
          </ul>

          <p className="text-foreground mb-4">
            Certains employés de Carré d'As Tutorat auront accès aux renseignements concernant un visiteur du site Web pour pouvoir répondre aux besoins de ce dernier et lui fournir l'information demandée sur des produits précis. Les employés de Carré d'As Tutorat ont comme directive de suivre des normes rigoureuses lors du traitement des renseignements personnels et confidentiels.
          </p>

          <p className="text-foreground mb-4">
            Les renseignements obtenus lors de l'enregistrement sur ce site Web ou la participation à un événement de Carré d'As Tutorat sont gardés sur une base de données interne chez Carré d'As Tutorat.
          </p>

          <p className="text-foreground mb-4">
            Si vous voulez que vos renseignements soient retirés de la base de données de Carré d'As Tutorat, prière de transmettre votre demande à <a href="mailto:info@carredastutorat.com" className="text-primary hover:underline">info@carredastutorat.com</a>.
          </p>
        </article>
      </div>
      <Footer />
    </div>
  );
}

