import { useState } from 'react';
import { CourseSelection } from './components/CourseSelection';
import { HelpTypeSelection } from './components/HelpTypeSelection';
import { WhenNeededSelection } from './components/WhenNeededSelection';
import { PersonalInfo } from './components/PersonalInfo';
import { ThankYou } from './components/ThankYou';
import { FormData, Step } from './types';

function App() {
  const [currentStep, setCurrentStep] = useState<Step>('course');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormData>({
    course: '',
    helpTypes: [],
    whenNeeded: '',
    name: '',
    email: ''
  });

  const updateFormData = (field: keyof FormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitForm = async () => {
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      const webhookUrl = import.meta.env.VITE_MAKE_WEBHOOK_URL;
      
      if (!webhookUrl) {
        throw new Error('Webhook URL not configured');
      }

      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          course: formData.course,
          helpTypes: formData.helpTypes,
          whenNeeded: formData.whenNeeded,
          name: formData.name,
          email: formData.email,
          timestamp: new Date().toISOString(),
          source: 'carre-das-questionnaire'
        })
      });

      if (!response.ok) {
        throw new Error(`Webhook failed with status: ${response.status}`);
      }

      // Success - proceed to thank you page
      setCurrentStep('thank-you');
    } catch (error) {
      console.error('Error submitting form:', error);
      setSubmitError(error instanceof Error ? error.message : 'Une erreur est survenue lors de l\'envoi');
      
      // Still proceed to thank you page after a delay to show the error
      setTimeout(() => {
        setCurrentStep('thank-you');
      }, 3000);
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => {
    switch (currentStep) {
      case 'course':
        setCurrentStep('helpType');
        break;
      case 'helpType':
        setCurrentStep('when');
        break;
      case 'when':
        setCurrentStep('name');
        break;
      case 'name':
        setCurrentStep('email');
        break;
      case 'email':
        if (!isSubmitting) {
          submitForm();
        }
        break;
    }
  };

  const prevStep = () => {
    switch (currentStep) {
      case 'helpType':
        setCurrentStep('course');
        break;
      case 'when':
        setCurrentStep('helpType');
        break;
      case 'name':
        setCurrentStep('when');
        break;
      case 'email':
        setCurrentStep('name');
        break;
    }
  };

  switch (currentStep) {
    case 'course':
      return (
        <CourseSelection
          onSelect={(course) => updateFormData('course', course)}
          onNext={nextStep}
        />
      );

    case 'helpType':
      return (
        <HelpTypeSelection
          selectedTypes={formData.helpTypes}
          onSelect={(types) => updateFormData('helpTypes', types)}
          onNext={nextStep}
          onBack={prevStep}
        />
      );

    case 'when':
      return (
        <WhenNeededSelection
          selectedWhen={formData.whenNeeded}
          onSelect={(when) => updateFormData('whenNeeded', when)}
          onNext={nextStep}
          onBack={prevStep}
        />
      );

    case 'name':
      return (
        <PersonalInfo
          currentField="name"
          name={formData.name}
          email={formData.email}
          onUpdate={updateFormData}
          onNext={nextStep}
          onBack={prevStep}
        />
      );

    case 'email':
      return (
        <PersonalInfo
          currentField="email"
          name={formData.name}
          email={formData.email}
          onUpdate={updateFormData}
          onNext={nextStep}
          onBack={prevStep}
          isSubmitting={isSubmitting}
          submitError={submitError}
        />
      );

    case 'thank-you':
      return <ThankYou />;

    default:
      return null;
  }
}

export default App;