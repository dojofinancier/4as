import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Questionnaire } from './components/Questionnaire';
import { NotFound } from './components/NotFound';
import { TutorApplication } from './components/TutorApplication';
import { TutorThankYou } from './components/TutorThankYou';

function App() {
  return (
    <Router>
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