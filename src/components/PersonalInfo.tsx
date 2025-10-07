import React, { useState, useEffect } from 'react';
import { ProgressBar } from './ProgressBar';

interface PersonalInfoProps {
  onUpdate: (field: 'name' | 'email', value: string) => void;
  onNext: (emailValue?: string) => void;
  onBack: () => void;
  name: string;
  email: string;
  currentField: 'name' | 'email';
  isSubmitting?: boolean;
  submitError?: string | null;
}

export function PersonalInfo({ onUpdate, onNext, onBack, name, email, currentField, isSubmitting = false, submitError }: PersonalInfoProps) {
  const [value, setValue] = useState(() => {
    if (currentField === 'name') {
      return name;
    } else {
      return email;
    }
  });

  // Reset value when currentField changes
  useEffect(() => {
    if (currentField === 'name') {
      setValue(name);
    } else {
      setValue(email);
    }
  }, [currentField, name, email]);
  
  const isName = currentField === 'name';
  const title = isName ? 'Comment vous appelez-vous ?' : 'Quelle est votre adresse email ?';
  const placeholder = isName ? 'Votre nom complet' : 'votre@email.com';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      console.log(`Updating ${currentField} with value:`, value.trim());
      onUpdate(currentField, value.trim());
      // For email field, pass the value directly to onNext to avoid state timing issues
      if (currentField === 'email') {
        onNext(value.trim());
      } else {
        onNext();
      }
    }
  };

  const isValid = isName ? value.trim().length > 0 : /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  
  // Debug: Log validation status for email
  if (!isName) {
    console.log(`Email validation - value: "${value}", isValid: ${isValid}`);
  }

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
        <ProgressBar currentStep={currentField} />
        
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            {title}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="mb-12">
          <input
            type={isName ? 'text' : 'email'}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={placeholder}
            className="w-full py-6 px-6 text-xl border-2 border-gray-200 rounded-2xl focus:border-[#00746b] focus:outline-none transition-colors"
            autoFocus
          />
        </form>

        <div className="flex justify-between">
          <button
            onClick={onBack}
            disabled={isSubmitting}
            className="text-gray-600 hover:text-gray-800 disabled:text-gray-400 font-medium py-3 px-8 transition-colors"
          >
            Retour
          </button>
          <button
            onClick={handleSubmit}
            disabled={!isValid || isSubmitting}
            className="bg-[#00746b] hover:bg-[#005a52] disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-4 px-12 rounded-xl text-lg transition-colors"
          >
            {isSubmitting ? 'Envoi en cours...' : (isName ? 'Continuer' : 'Envoyer')}
          </button>
        </div>
        
        {submitError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm">
              {submitError}
            </p>
            <p className="text-red-600 text-xs mt-1">
              Vous serez redirigé automatiquement...
            </p>
          </div>
        )}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-4 text-gray-500 text-sm">
        © 2025 Carré d'As Tutorat. Tous droits réservés.
      </div>
    </div>
  );
}