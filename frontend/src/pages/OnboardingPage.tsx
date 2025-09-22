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
    <section>
      <h2>Welcome to Grant Matcher</h2>
      <p>Tell us about your organization to personalize the grants we recommend.</p>
      <UserOnboardingForm onSubmit={handleSubmit} />
    </section>
  );
};

export default OnboardingPage;
