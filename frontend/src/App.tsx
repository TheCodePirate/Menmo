import React, { useCallback, useEffect, useState } from 'react';
import { Link, Route, Routes } from 'react-router-dom';

import GrantSearchPage from './pages/GrantSearchPage';
import MatchesPage from './pages/MatchesPage';
import OnboardingPage from './pages/OnboardingPage';

const App: React.FC = () => {
  const [userId, setUserId] = useState<number | null>(() => {
    if (typeof window === 'undefined') {
      return null;
    }
    const stored = window.localStorage.getItem('menmo:user-id');
    return stored ? Number(stored) : null;
  });

  useEffect(() => {
    if (userId) {
      window.localStorage.setItem('menmo:user-id', String(userId));
    }
  }, [userId]);

  const handleProfileCreated = useCallback((id: number) => {
    setUserId(id);
    window.localStorage.setItem('menmo:user-id', String(id));
  }, []);

  const handleResetProfile = useCallback(() => {
    setUserId(null);
    window.localStorage.removeItem('menmo:user-id');
  }, []);

  return (
    <div className="app-container">
      <header>
        <h1>Grant Matcher</h1>
        <nav>
          <Link to="/">Onboarding</Link>
          <Link to="/grants">Grant search</Link>
          <Link to="/matches">Recommended matches</Link>
        </nav>
        {userId && (
          <button type="button" className="link-button" onClick={handleResetProfile}>
            Reset profile
          </button>
        )}
      </header>
      <main>
        <Routes>
          <Route
            path="/"
            element={<OnboardingPage onProfileCreated={handleProfileCreated} userId={userId} />}
          />
          <Route path="/grants" element={<GrantSearchPage />} />
          <Route path="/matches" element={<MatchesPage userId={userId} />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
