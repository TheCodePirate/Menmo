import axios from 'axios';
import React, { useEffect, useState } from 'react';

import GrantMatchList from '../components/GrantMatchList';
import { MatchResult } from '../types';

interface Props {
  userId: number | null;
}

const MatchesPage: React.FC<Props> = ({ userId }) => {
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchMatches = async () => {
      if (!userId) {
        setMatches([]);
        return;
      }
      setIsLoading(true);
      try {
        const response = await axios.get(`/api/matches/${userId}`);
        setMatches(response.data);
      } catch (error) {
        setMatches([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMatches();
  }, [userId]);

  if (!userId) {
    return <p>Create a user profile to unlock personalized matches.</p>;
  }

  return (
    <section>
      <h2>Recommended Matches</h2>
      <GrantMatchList matches={matches} isLoading={isLoading} />
    </section>
  );
};

export default MatchesPage;
