import React, { useState } from 'react';
import { Link, Route, Routes } from 'react-router-dom';

import GrantSearchPage from './pages/GrantSearchPage';
import MatchesPage from './pages/MatchesPage';
import OnboardingPage from './pages/OnboardingPage';

const App: React.FC = () => {
  const [userId, setUserId] = useState<number | null>(null);

  return (
    <div className="app-container">
      <header>
        <h1>Grant Matcher</h1>
        <nav>
          <Link to="/">Onboarding</Link>
          <Link to="/grants">Grant search</Link>
          <Link to="/matches">Recommended matches</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<OnboardingPage onProfileCreated={setUserId} />} />
          <Route path="/grants" element={<GrantSearchPage />} />
          <Route path="/matches" element={<MatchesPage userId={userId} />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
