import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { Questionnaire } from './components/Questionnaire';
import { NotFound } from './components/NotFound';
import { TutorApplication } from './components/TutorApplication';
import { TutorThankYou } from './components/TutorThankYou';
import { CourseBlogPost } from './components/CourseBlogPost';
import { GeneralArticle } from './components/GeneralArticle';
import { PolitiqueConfidentialite } from './components/PolitiqueConfidentialite';
import { TermesEtConditions } from './components/TermesEtConditions';
import { APropos } from './components/APropos';
import { BlogListing } from './components/BlogListing';
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
        
        {/* Legal and info pages */}
        <Route path="/a-propos" element={<APropos />} />
        <Route path="/politique-de-confidentialite" element={<PolitiqueConfidentialite />} />
        <Route path="/termes-et-conditions" element={<TermesEtConditions />} />
        
        {/* Blog listing */}
        <Route path="/blog" element={<BlogListing />} />
        
        {/* General article routes */}
        <Route path="/article/:slug" element={<GeneralArticle />} />
        
        {/* Blog post routes - dynamic slug for SEO-friendly URLs */}
        <Route path="/:slug" element={<CourseBlogPost />} />
        
        {/* Catch-all route for 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;