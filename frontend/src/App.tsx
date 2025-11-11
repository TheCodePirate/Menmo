import React, { useState } from 'react';
import { NavLink, Route, Routes } from 'react-router-dom';

import './App.css';

import GrantSearchPage from './pages/GrantSearchPage';
import MatchesPage from './pages/MatchesPage';
import OnboardingPage from './pages/OnboardingPage';

const App: React.FC = () => {
  const [userId, setUserId] = useState<number | null>(null);

  return (
    <div className="app-shell">
      <header className="app-header layout-width">
        <NavLink to="/" className="brand" end>
          <span className="brand-mark">menmo</span>
          <span className="brand-tagline">climate capital compass</span>
        </NavLink>
        <nav className="nav-links">
          <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
            Onboarding
          </NavLink>
          <NavLink to="/grants" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
            Grant search
          </NavLink>
          <NavLink to="/matches" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
            Recommended matches
          </NavLink>
        </nav>
      </header>
      <main className="app-main layout-width">
        <Routes>
          <Route path="/" element={<OnboardingPage onProfileCreated={setUserId} />} />
          <Route path="/grants" element={<GrantSearchPage />} />
          <Route path="/matches" element={<MatchesPage userId={userId} />} />
        </Routes>
      </main>
      <footer className="app-footer layout-width">
        <p>© {new Date().getFullYear()} Menmo.ai — intelligence for decisive climate funding.</p>
      </footer>
    </div>
  );
};

export default App;
