import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Questionnaire } from './components/Questionnaire';
import { NotFound } from './components/NotFound';

function App() {
  return (
    <Router>
      <Routes>
        {/* Main questionnaire route */}
        <Route path="/" element={<Questionnaire />} />
        
        {/* Catch-all route for 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;