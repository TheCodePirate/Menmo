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
    return (
      <section className="page-shell content-card">
        <div className="section-heading">
          <span className="eyebrow">Intelligence feed</span>
          <h2>Recommended Matches</h2>
          <p>Create a Menmo profile to reveal precision-matched opportunities and next actions.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="page-shell content-card">
      <div className="section-heading">
        <span className="eyebrow">Intelligence feed</span>
        <h2>Recommended Matches</h2>
        <p>We surface the highest-signal grants with transparent scores and reasons to pursue.</p>
      </div>
      <GrantMatchList matches={matches} isLoading={isLoading} />
    </section>
  );
};

export default MatchesPage;
