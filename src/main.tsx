import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { initGA } from './lib/analytics';

// Initialize Google Analytics if measurement ID is provided
const gaMeasurementId = import.meta.env.VITE_GA_MEASUREMENT_ID;
if (gaMeasurementId) {
  initGA(gaMeasurementId);
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
