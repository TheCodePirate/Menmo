import axios from 'axios';
import React from 'react';

import UserOnboardingForm from '../components/UserOnboardingForm';
import { UserProfilePayload } from '../types';

interface Props {
  onProfileCreated: (userId: number) => void;
}

const OnboardingPage: React.FC<Props> = ({ onProfileCreated }) => {
  const handleSubmit = async (payload: UserProfilePayload) => {
    const response = await axios.post('/api/users', payload);
    onProfileCreated(response.data.id);
  };

  return (
    <section className="page-shell landing-grid">
      <div className="landing-copy">
        <span className="eyebrow">menmo.ai</span>
        <h1>Climate capital intelligence, distilled.</h1>
        <p>
          Menmo orchestrates grant intelligence, application guidance, and governance into a single
          minimalist workspace so climate teams can move from idea to funded execution with clarity.
        </p>
        <div className="signal-grid">
          <span className="signal-pill">Instant climate-fit scoring</span>
          <span className="signal-pill">Gap-to-Yes playbooks</span>
          <span className="signal-pill">Deadline radar &amp; evidence vault</span>
        </div>
      </div>
      <div className="onboarding-card">
        <h2>Start the climate readiness scan</h2>
        <p className="card-subtitle">
          Share a few details about your organisation and impact focus to unlock precision matches and
          guided next steps.
        </p>
        <UserOnboardingForm onSubmit={handleSubmit} />
        <p className="card-footnote">~3 minutes. Human-readable outputs. Zero fluff.</p>
      </div>
    </section>
  );
};

export default OnboardingPage;
