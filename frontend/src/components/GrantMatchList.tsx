import React from 'react';

import { MatchResult } from '../types';

interface Props {
  matches: MatchResult[];
  isLoading?: boolean;
}

const GrantMatchList: React.FC<Props> = ({ matches, isLoading }) => {
  if (isLoading) {
    return <p>Loading recommended matches...</p>;
  }

  if (!matches.length) {
    return <p>No matches yet. Complete onboarding and ingest grants to see recommendations.</p>;
  }

  return (
    <ul className="grant-match-list">
      {matches.map((match) => (
        <li key={match.grant.id} className="grant-match">
          <h3>{match.grant.title}</h3>
          {match.grant.sponsor && <p className="sponsor">Sponsored by {match.grant.sponsor}</p>}
          <p>{match.grant.description}</p>
          <p className="score">Match score: {(match.score * 100).toFixed(1)}%</p>
          {match.grant.url && (
            <a href={match.grant.url} target="_blank" rel="noreferrer">
              View grant details
            </a>
          )}
        </li>
      ))}
    </ul>
  );
};

export default GrantMatchList;
