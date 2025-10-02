import { useState } from 'react';
import { ProgressBar } from './ProgressBar';

interface WhenNeededSelectionProps {
  onSelect: (when: string) => void;
  onNext: () => void;
  onBack: () => void;
  selectedWhen: string;
}

const timeOptions = [
  'Dès que possible',
  'Dans les 24 heures',
  'Dans les 3 jours',
  'Dans une semaine',
  'Flexible'
];

export function WhenNeededSelection({ onSelect, onNext, onBack, selectedWhen }: WhenNeededSelectionProps) {
  const [selected, setSelected] = useState(selectedWhen);

  const handleSelect = (option: string) => {
    setSelected(option);
    onSelect(option);
  };

  const handleNext = () => {
    if (selected) {
      onNext();
    }
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
        <div className="max-w-2xl w-full">
        <ProgressBar currentStep="when" />
        
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Quand avez-vous besoin d'aide ?
          </h2>
          <p className="text-lg text-gray-600">Sélectionnez la période souhaitée</p>
        </div>

        <div className="space-y-4 mb-12">
          {timeOptions.map((option) => (
            <button
              key={option}
              onClick={() => handleSelect(option)}
              className={`w-full p-6 rounded-xl border-2 transition-all text-left ${
                selected === option
                  ? 'border-[#00746b] bg-[#00746b]/5'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <span className={`text-lg font-medium ${
                selected === option ? 'text-[#00746b]' : 'text-gray-700'
              }`}>
                {option}
              </span>
            </button>
          ))}
        </div>

        <div className="flex justify-between">
          <button
            onClick={onBack}
            className="text-gray-600 hover:text-gray-800 font-medium py-3 px-8 transition-colors"
          >
            Retour
          </button>
          <button
            onClick={handleNext}
            disabled={!selected}
            className="bg-[#00746b] hover:bg-[#005a52] disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-4 px-12 rounded-xl text-lg transition-colors"
          >
            Continuer
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