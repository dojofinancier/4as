/**
 * Web Vitals monitoring
 * Measures Core Web Vitals: LCP, CLS, INP
 */

import { reportWebVitals } from './analytics';

type Metric = {
  name: string;
  value: number;
  id: string;
  delta: number;
  rating: 'good' | 'needs-improvement' | 'poor';
};

/**
 * Get rating for a metric value
 */
function getRating(name: string, value: number): 'good' | 'needs-improvement' | 'poor' {
  const thresholds: Record<string, { good: number; poor: number }> = {
    LCP: { good: 2500, poor: 4000 },
    CLS: { good: 0.1, poor: 0.25 },
    INP: { good: 200, poor: 500 },
    FID: { good: 100, poor: 300 },
  };

  const threshold = thresholds[name];
  if (!threshold) return 'good';

  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

/**
 * Measure Largest Contentful Paint (LCP)
 */
function measureLCP() {
  if (typeof window === 'undefined' || !('PerformanceObserver' in window)) return;

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1] as any;
      
      const metric: Metric = {
        name: 'LCP',
        value: lastEntry.renderTime || lastEntry.loadTime,
        id: lastEntry.id || 'lcp',
        delta: lastEntry.renderTime || lastEntry.loadTime,
        rating: getRating('LCP', lastEntry.renderTime || lastEntry.loadTime),
      };

      reportWebVitals(metric);
      observer.disconnect();
    });

    observer.observe({ entryTypes: ['largest-contentful-paint'] });
  } catch (e) {
    // PerformanceObserver not supported
  }
}

/**
 * Measure Cumulative Layout Shift (CLS)
 */
function measureCLS() {
  if (typeof window === 'undefined' || !('PerformanceObserver' in window)) return;

  let clsValue = 0;
  let clsEntries: any[] = [];

  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
          clsEntries.push(entry);
        }
      }
    });

    observer.observe({ entryTypes: ['layout-shift'] });

    // Report CLS when page is hidden
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden' && clsValue > 0) {
        const metric: Metric = {
          name: 'CLS',
          value: clsValue,
          id: 'cls',
          delta: clsValue,
          rating: getRating('CLS', clsValue),
        };
        reportWebVitals(metric);
        observer.disconnect();
      }
    });
  } catch (e) {
    // PerformanceObserver not supported
  }
}

/**
 * Measure Interaction to Next Paint (INP)
 */
function measureINP() {
  if (typeof window === 'undefined' || !('PerformanceObserver' in window)) return;

  let inpValue = 0;
  let inpEntries: any[] = [];

  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if ((entry as any).duration) {
          inpValue = Math.max(inpValue, (entry as any).duration);
          inpEntries.push(entry);
        }
      }
    });

    observer.observe({ entryTypes: ['event'] });

    // Report INP when page is hidden
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden' && inpValue > 0) {
        const metric: Metric = {
          name: 'INP',
          value: inpValue,
          id: 'inp',
          delta: inpValue,
          rating: getRating('INP', inpValue),
        };
        reportWebVitals(metric);
        observer.disconnect();
      }
    });
  } catch (e) {
    // PerformanceObserver not supported
  }
}

/**
 * Initialize Web Vitals monitoring
 */
export function initWebVitals() {
  if (typeof window === 'undefined') return;

  // Wait for page load
  if (document.readyState === 'complete') {
    measureLCP();
    measureCLS();
    measureINP();
  } else {
    window.addEventListener('load', () => {
      measureLCP();
      measureCLS();
      measureINP();
    });
  }
}

