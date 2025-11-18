import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { CourseSelection } from './CourseSelection';
import { HelpTypeSelection } from './HelpTypeSelection';
import { WhenNeededSelection } from './WhenNeededSelection';
import { PersonalInfo } from './PersonalInfo';
import { ThankYou } from './ThankYou';
import { FormData, Step } from '../types';
import { checkCourseAvailability } from '../lib/supabase';

export function Questionnaire() {
  const location = useLocation();
  const [currentStep, setCurrentStep] = useState<Step>('course');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormData>({
    course: '', // For webhook (full text display)
    courseCode: '', // For availability check
    courseSlug: null, // For redirect
    courseDisplayText: '', // For display/webhook
    courseTitle: '', // Course title only (without code/institution)
    courseActive: undefined, // Whether the course is active
    helpTypes: [],
    whenNeeded: '',
    name: '',
    email: ''
  });

  const updateFormData = (field: keyof FormData, value: any) => {
    console.log(`Updating form data - field: ${field}, value:`, value);
    setFormData(prev => {
      const newData = {
        ...prev,
        [field]: value
      };
      console.log('New form data:', newData);
      return newData;
    });
  };

  // Handle pre-selected course from article CTA
  useEffect(() => {
    const selectedCourse = (location.state as any)?.selectedCourse;
    if (selectedCourse) {
      // Pre-populate form data with selected course
      updateFormData('courseCode', selectedCourse.code);
      updateFormData('courseSlug', selectedCourse.slug);
      updateFormData('courseDisplayText', selectedCourse.displayText);
      updateFormData('courseTitle', selectedCourse.title);
      updateFormData('course', selectedCourse.displayText);
      updateFormData('courseActive', selectedCourse.active);
      
      // Automatically move to next step (helpType) since course is already selected
      setCurrentStep('helpType');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  const submitForm = async (emailValue?: string) => {
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      const webhookUrl = import.meta.env.VITE_MAKE_WEBHOOK_URL;
      
      if (!webhookUrl) {
        throw new Error('Webhook URL not configured');
      }

      // Use the passed email value or fall back to formData.email
      const emailToSend = emailValue || formData.email;

      // Debug: Log the form data being sent
      console.log('Form data being sent to webhook:', {
        course: formData.course,
        helpTypes: formData.helpTypes,
        whenNeeded: formData.whenNeeded,
        name: formData.name,
        email: emailToSend,
        timestamp: new Date().toISOString(),
        source: 'carre-das-questionnaire'
      });

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
          email: emailToSend,
          timestamp: new Date().toISOString(),
          source: 'carre-das-questionnaire'
        })
      });

      if (!response.ok) {
        throw new Error(`Webhook failed with status: ${response.status}`);
      }

      // Success - check course availability and redirect if available
      try {
        // If course is inactive, assume no tutors and show thank you page
        if (formData.courseActive === false) {
          setCurrentStep('thank-you');
          return;
        }
        
        // For active courses, check availability and redirect if available
        const availability = await checkCourseAvailability(formData.courseCode);
        
        if (availability.available && availability.slug) {
          // Redirect to app reservation page
          window.location.href = `https://app.carredastutorat.com/cours/${availability.slug}/reservation?code=${encodeURIComponent(formData.courseCode)}&source=lp`;
          return; // Don't proceed to thank you page
        } else {
          // Course is not available (no tutors) - show thank you page
          setCurrentStep('thank-you');
        }
      } catch (availabilityError) {
        // If availability check fails, show thank you page (graceful degradation)
        console.error('Availability check error:', availabilityError);
        setCurrentStep('thank-you');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setSubmitError(error instanceof Error ? error.message : 'Une erreur est survenue lors de l\'envoi');
      
      // Still proceed to thank you page after a delay to show the error
      // (graceful degradation - availability check won't happen on webhook error)
      setTimeout(() => {
        setCurrentStep('thank-you');
      }, 3000);
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = (emailValue?: string) => {
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
          // If email value is passed directly, use it instead of formData.email
          if (emailValue) {
            submitForm(emailValue);
          } else {
            submitForm();
          }
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
          onSelect={(course) => {
            // Store all course data fields
            updateFormData('courseCode', course.code);
            updateFormData('courseSlug', course.slug);
            updateFormData('courseDisplayText', course.displayText);
            updateFormData('courseTitle', course.title);
            updateFormData('course', course.displayText); // For webhook backward compatibility
            updateFormData('courseActive', course.active);
          }}
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
      return <ThankYou courseName={formData.courseTitle} onBackToSearch={() => setCurrentStep('course')} />;

    default:
      return null;
  }
}
