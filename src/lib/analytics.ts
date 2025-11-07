// Google Analytics utility functions

declare global {
  interface Window {
    gtag: (
      command: 'config' | 'event' | 'js' | 'set',
      targetId: string | Date,
      config?: Record<string, any>
    ) => void;
    dataLayer: any[];
  }
}

/**
 * Initialize Google Analytics with the measurement ID
 */
export function initGA(measurementId: string) {
  if (typeof window === 'undefined' || !measurementId) {
    return;
  }

  // Load the gtag script
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  document.head.appendChild(script);

  // Initialize gtag
  window.dataLayer = window.dataLayer || [];
  window.gtag = function() {
    window.dataLayer.push(arguments);
  };
  window.gtag('js', new Date());
  window.gtag('config', measurementId);
}

/**
 * Track a custom event
 */
export function trackEvent(
  eventName: string,
  eventParams?: {
    [key: string]: any;
  }
) {
  if (typeof window === 'undefined' || !window.gtag) {
    return;
  }

  window.gtag('event', eventName, eventParams);
}

/**
 * Track page view
 */
export function trackPageView(path: string, title?: string) {
  if (typeof window === 'undefined' || !window.gtag) {
    return;
  }

  const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID;
  if (!measurementId) return;

  window.gtag('config', measurementId, {
    page_path: path,
    page_title: title,
  });
}

