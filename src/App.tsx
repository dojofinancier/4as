import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { Questionnaire } from './components/Questionnaire';
import { NotFound } from './components/NotFound';
import { TutorApplication } from './components/TutorApplication';
import { TutorThankYou } from './components/TutorThankYou';
import { trackPageView } from './lib/analytics';

// Component to track page views on route changes
function PageViewTracker() {
  const location = useLocation();

  useEffect(() => {
    trackPageView(location.pathname + location.search, document.title);
  }, [location]);

  return null;
}

function App() {
  return (
    <Router>
      <PageViewTracker />
      <Routes>
        {/* Main questionnaire route */}
        <Route path="/" element={<Questionnaire />} />
        
        {/* Tutor application routes */}
        <Route path="/devenez-tuteur" element={<TutorApplication />} />
        <Route path="/devenez-tuteur/merci" element={<TutorThankYou />} />
        
        {/* Catch-all route for 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;