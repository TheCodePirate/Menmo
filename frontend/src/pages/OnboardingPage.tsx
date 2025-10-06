import axios from 'axios';
import React from 'react';

import UserOnboardingForm from '../components/UserOnboardingForm';
import { UserProfile, UserProfilePayload } from '../types';

interface Props {
  onProfileCreated: (userId: number) => void;
  userId?: number | null;
}

const OnboardingPage: React.FC<Props> = ({ onProfileCreated, userId }) => {
  const [existingProfile, setExistingProfile] = React.useState<UserProfile | null>(null);

  React.useEffect(() => {
    const fetchProfile = async () => {
      if (!userId) {
        setExistingProfile(null);
        return;
      }
      try {
        const response = await axios.get(`/api/users/${userId}`);
        setExistingProfile(response.data);
      } catch (error) {
        setExistingProfile(null);
      }
    };

    fetchProfile();
  }, [userId]);

  const handleSubmit = async (payload: UserProfilePayload) => {
    const response = await axios.post('/api/users', payload);
    onProfileCreated(response.data.id);
  };

  return (
    <section>
      <h2>Welcome to Grant Matcher</h2>
      <p>Tell us about your organization to personalize the grants we recommend.</p>
      {existingProfile && (
        <aside className="status">
          <p>
            You already have a saved profile for <strong>{existingProfile.organization || existingProfile.name}</strong>.
            Update the details below to create an additional profile or reset from the header to start fresh.
          </p>
        </aside>
      )}
      <UserOnboardingForm onSubmit={handleSubmit} />
    </section>
  );
};

export default OnboardingPage;
