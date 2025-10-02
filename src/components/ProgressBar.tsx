import { Step } from '../types';

interface ProgressBarProps {
  currentStep: Step;
}

const steps: Step[] = ['course', 'helpType', 'when', 'name', 'email'];

export function ProgressBar({ currentStep }: ProgressBarProps) {
  const currentIndex = steps.indexOf(currentStep);
  const progress = ((currentIndex + 1) / steps.length) * 100;

  return (
    <div className="w-full max-w-md mx-auto mb-8">
      <div className="flex justify-between text-sm text-gray-600 mb-2">
        <span>Question {currentIndex + 1} sur {steps.length}</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-[#00746b] h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
}