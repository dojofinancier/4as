import React, { useState } from 'react';
import { supabase } from '../lib/supabase';
import { TutorApplicationData } from '../types';

const DOMAINES_ETUDE = [
  'Comptabilité',
  'Finance', 
  'Économie',
  'Mathématiques & Statistiques',
  'Gestion des opérations',
  'Management',
  'Autre'
];

const NIVEAUX_ETUDE = [
  'Baccalauréat (en cours)',
  'Baccalauréat',
  'Maîtrise',
  'Doctorat'
];

const DISPONIBILITES = [
  'Jours',
  'Soirs', 
  'Weekends'
];

export function TutorApplication() {
  const [formData, setFormData] = useState<TutorApplicationData>({
    prenom: '',
    nom: '',
    email: '',
    telephone: '',
    domaineEtude: [],
    autreDomaine: '',
    niveauEtude: '',
    disponibilites: [],
    experienceTutorat: '',
    cvFile: undefined,
    cvUrl: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [showAutreField, setShowAutreField] = useState(false);

  const updateFormData = (field: keyof TutorApplicationData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDomaineChange = (domaine: string, checked: boolean) => {
    if (checked) {
      updateFormData('domaineEtude', [...formData.domaineEtude, domaine]);
      if (domaine === 'Autre') {
        setShowAutreField(true);
      }
    } else {
      updateFormData('domaineEtude', formData.domaineEtude.filter(d => d !== domaine));
      if (domaine === 'Autre') {
        setShowAutreField(false);
        updateFormData('autreDomaine', '');
      }
    }
  };

  const handleDisponibiliteChange = (dispo: string, checked: boolean) => {
    if (checked) {
      updateFormData('disponibilites', [...formData.disponibilites, dispo]);
    } else {
      updateFormData('disponibilites', formData.disponibilites.filter(d => d !== dispo));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      updateFormData('cvFile', file);
    }
  };

  const uploadCV = async (file: File): Promise<string> => {
    // Convert file to base64 for webhook transmission
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        resolve(base64);
      };
      reader.onerror = () => {
        reject(new Error('Erreur lors de la lecture du fichier CV'));
      };
      reader.readAsDataURL(file);
    });
  };

  const isFormValid = () => {
    const hasAutreDomaine = formData.domaineEtude.includes('Autre');
    const autreDomaineValid = !hasAutreDomaine || (hasAutreDomaine && formData.autreDomaine?.trim());
    
    return (
      formData.prenom.trim() &&
      formData.nom.trim() &&
      formData.email.trim() &&
      formData.telephone.trim() &&
      formData.domaineEtude.length > 0 &&
      autreDomaineValid &&
      formData.niveauEtude &&
      formData.disponibilites.length > 0 &&
      formData.experienceTutorat
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isFormValid()) {
      setSubmitError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Convert CV to base64 if provided
      let cvData = null;
      if (formData.cvFile) {
        cvData = await uploadCV(formData.cvFile);
      }

      // Prepare data for webhook
      const webhookData = {
        prenom: formData.prenom,
        nom: formData.nom,
        email: formData.email,
        telephone: formData.telephone,
        domaineEtude: formData.domaineEtude,
        autreDomaine: formData.autreDomaine,
        niveauEtude: formData.niveauEtude,
        disponibilites: formData.disponibilites,
        experienceTutorat: formData.experienceTutorat,
        cvFileName: formData.cvFile?.name || null,
        cvFileData: cvData, // Base64 encoded file data
        cvFileType: formData.cvFile?.type || null,
        timestamp: new Date().toISOString(),
        source: 'carre-das-tutor-application'
      };

      // Send to Make.com webhook
      const webhookUrl = import.meta.env.VITE_MAKE_TUTOR_WEBHOOK_URL;
      
      if (!webhookUrl) {
        throw new Error('Webhook URL not configured');
      }

      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(webhookData)
      });

      if (!response.ok) {
        throw new Error(`Webhook failed with status: ${response.status}`);
      }

      // Redirect to thank you page
      window.location.href = '/devenez-tuteur/merci';
      
    } catch (error) {
      console.error('Error submitting tutor application:', error);
      setSubmitError(error instanceof Error ? error.message : 'Une erreur est survenue lors de l\'envoi');
    } finally {
      setIsSubmitting(false);
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
      <div className="flex-1 p-4 pt-20">
        <div className="max-w-4xl mx-auto">
          {/* Company Description */}
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-8 text-center">
              Devenez tuteur
            </h1>
            
            <div className="prose prose-lg max-w-none">
              <p className="text-xl text-gray-700 mb-6">
                Carré d'As est toujours à la recherche de tuteurs motivés. N'hésitez pas à poser votre candidature si vous croyez avoir ce qu'il faut pour aider les étudiants!
              </p>

              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Ce que nous offrons</h3>
              <p className="text-gray-700 mb-4">
                Si vous avez un bac, maîtrise ou doctorat dans un domaine de l'administration (comptabilité, finance, gestion, économie, etc.), le tutorat est un excellent tremplin pour votre carrière et un moyen de faire de l'argent à temps partiel.
              </p>
              <p className="text-gray-700 mb-4">
                La plupart de nos tuteurs sont soit aux études aux cycles supérieurs ou ont déjà un travail et font du tutorat à temps partiel.
              </p>
              <p className="text-gray-700 mb-4">Au delà de la rémunération, devenir tuteur est un excellent moyen de:</p>
              <ul className="list-disc list-inside text-gray-700 mb-6 space-y-2">
                <li>Acquérir de l'expérience d'enseignement. Plusieurs de nos anciens tuteurs sont devenus professeurs au collégial et à l'université.</li>
                <li>Développer votre pédagogie. Rares sont les carrières qui ne nécessitent pas de communiquer, vulgariser et expliquer des concepts.</li>
                <li>Approfondir vos connaissances dans votre domaine. Le fait de devoir déconstruire et expliquer la matière permet de revoir les bases.</li>
              </ul>

              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Ce que nous cherchons</h3>
              <p className="text-gray-700 mb-4">
                Les candidats que nous voulons sont enthousiastes, empathiques et humbles. Les tuteurs qui ont de bonnes évaluations sont ceux qui ont une ouverture d'esprit et sont capables de comprendre l'étudiant pour ensuite le guider vers la compréhension du matériel.
              </p>
              <p className="text-gray-700 mb-6">
                Par contre, nous croyons en une approche évolutive donc pas besoin d'être le tuteur parfait pour appliquer. Vous n'avez pas non plus besoin d'expérience de tutorat. Remplissez le formulaire pour appliquer!
              </p>
            </div>
          </div>

          {/* Application Form */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
              Formulaire de candidature
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prénom *
                  </label>
                  <input
                    type="text"
                    value={formData.prenom}
                    onChange={(e) => updateFormData('prenom', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00746b] focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nom *
                  </label>
                  <input
                    type="text"
                    value={formData.nom}
                    onChange={(e) => updateFormData('nom', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00746b] focus:border-transparent"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Courriel *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => updateFormData('email', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00746b] focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Téléphone *
                  </label>
                  <input
                    type="tel"
                    value={formData.telephone}
                    onChange={(e) => updateFormData('telephone', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00746b] focus:border-transparent"
                    required
                  />
                </div>
              </div>

              {/* Study Domain */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Domaine d'étude *
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {DOMAINES_ETUDE.map((domaine) => (
                    <label key={domaine} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.domaineEtude.includes(domaine)}
                        onChange={(e) => handleDomaineChange(domaine, e.target.checked)}
                        className="mr-2 h-4 w-4 text-[#00746b] focus:ring-[#00746b] border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700">{domaine}</span>
                    </label>
                  ))}
                </div>
                {showAutreField && (
                  <div className="mt-3">
                    <input
                      type="text"
                      value={formData.autreDomaine || ''}
                      onChange={(e) => updateFormData('autreDomaine', e.target.value)}
                      placeholder="Spécifiez votre domaine d'étude"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00746b] focus:border-transparent"
                      required
                    />
                  </div>
                )}
              </div>

              {/* Education Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dernier niveau d'étude complété *
                </label>
                <select
                  value={formData.niveauEtude}
                  onChange={(e) => updateFormData('niveauEtude', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00746b] focus:border-transparent"
                  required
                >
                  <option value="">Sélectionnez un niveau</option>
                  {NIVEAUX_ETUDE.map((niveau) => (
                    <option key={niveau} value={niveau}>{niveau}</option>
                  ))}
                </select>
              </div>

              {/* Availability */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Disponibilités pour du tutorat *
                </label>
                <div className="flex flex-wrap gap-4">
                  {DISPONIBILITES.map((dispo) => (
                    <label key={dispo} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.disponibilites.includes(dispo)}
                        onChange={(e) => handleDisponibiliteChange(dispo, e.target.checked)}
                        className="mr-2 h-4 w-4 text-[#00746b] focus:ring-[#00746b] border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700">{dispo}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Tutoring Experience */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Avez-vous déjà fait du tutorat rémunéré dans les 3 dernières années? *
                </label>
                <div className="flex gap-6">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="experienceTutorat"
                      value="oui"
                      checked={formData.experienceTutorat === 'oui'}
                      onChange={(e) => updateFormData('experienceTutorat', e.target.value)}
                      className="mr-2 h-4 w-4 text-[#00746b] focus:ring-[#00746b] border-gray-300"
                    />
                    <span className="text-sm text-gray-700">Oui</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="experienceTutorat"
                      value="non"
                      checked={formData.experienceTutorat === 'non'}
                      onChange={(e) => updateFormData('experienceTutorat', e.target.value)}
                      className="mr-2 h-4 w-4 text-[#00746b] focus:ring-[#00746b] border-gray-300"
                    />
                    <span className="text-sm text-gray-700">Non</span>
                  </label>
                </div>
              </div>

              {/* CV Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Votre CV
                </label>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00746b] focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-[#00746b] file:text-white hover:file:bg-[#005a52]"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Formats acceptés: PDF, DOC, DOCX (max 10MB)
                </p>
              </div>

              {/* Submit Button */}
              <div className="pt-6">
                <button
                  type="submit"
                  disabled={!isFormValid() || isSubmitting}
                  className="w-full bg-[#00746b] hover:bg-[#005a52] disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-4 px-8 rounded-xl text-lg transition-colors"
                >
                  {isSubmitting ? 'Envoi en cours...' : 'Soumettre ma candidature'}
                </button>
              </div>

              {submitError && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-700 text-sm">{submitError}</p>
                </div>
              )}
            </form>
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
