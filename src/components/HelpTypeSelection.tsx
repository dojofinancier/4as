import { useState } from 'react';
import { Check } from 'lucide-react';
import { ProgressBar } from './ProgressBar';
import { Footer } from './Footer';

interface HelpTypeSelectionProps {
  onSelect: (types: string[]) => void;
  onNext: () => void;
  onBack: () => void;
  selectedTypes: string[];
}

const helpTypes = [
  'Aide aux devoirs',
  'Préparation aux examens',
  'Explication de concepts',
  'Révision de cours',
  'Travaux pratiques'
];

export function HelpTypeSelection({ onSelect, onNext, onBack, selectedTypes }: HelpTypeSelectionProps) {
  const [selected, setSelected] = useState<string[]>(selectedTypes);

  const toggleType = (type: string) => {
    const newSelected = selected.includes(type)
      ? selected.filter(t => t !== type)
      : [...selected, type];
    setSelected(newSelected);
    onSelect(newSelected);
  };

  const handleNext = () => {
    if (selected.length > 0) {
      onNext();
    }
  };

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
        <div className="max-w-2xl w-full">
        <ProgressBar currentStep="helpType" />
        
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Quel type d'aide recherchez-vous ?
          </h2>
          <p className="text-lg text-muted-foreground">Sélectionnez une ou plusieurs options</p>
        </div>

        <div className="space-y-4 mb-12">
          {helpTypes.map((type) => (
            <button
              key={type}
              onClick={() => toggleType(type)}
              className={`w-full p-6 rounded-xl border-2 transition-all text-left flex items-center justify-between ${
                selected.includes(type)
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <span className={`text-lg font-medium ${
                selected.includes(type) ? 'text-primary' : 'text-foreground/90'
              }`}>
                {type}
              </span>
              {selected.includes(type) && (
                <Check className="h-6 w-6 text-primary" />
              )}
            </button>
          ))}
        </div>

        <div className="flex justify-between">
          <button
            onClick={onBack}
            className="text-muted-foreground hover:text-foreground font-medium py-3 px-8 transition-colors"
          >
            Retour
          </button>
          <button
            onClick={handleNext}
            disabled={selected.length === 0}
            className="bg-primary hover:bg-primary/90 disabled:bg-muted disabled:cursor-not-allowed text-primary-foreground font-semibold py-4 px-12 rounded-xl text-lg transition-colors border-2 border-primary disabled:border-muted"
          >
            Continuer
          </button>
        </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}