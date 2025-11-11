import React from 'react';

import { MatchResult } from '../types';

interface Props {
  matches: MatchResult[];
  isLoading?: boolean;
}

const GrantMatchList: React.FC<Props> = ({ matches, isLoading }) => {
  if (isLoading) {
    return <p className="card-state">Loading recommended matches...</p>;
  }

  if (!matches.length) {
    return (
      <p className="card-state">
        No matches yet. Complete onboarding and ingest grants to surface precision-aligned opportunities.
      </p>
    );
  }

  return (
    <ul className="grant-match-list">
      {matches.map((match) => (
        <li key={match.grant.id} className="grant-match">
          <div className="match-score">
            <span className="score-value">{(match.score * 100).toFixed(0)}%</span>
            <span className="score-label">fit</span>
          </div>
          <div className="match-body">
            <h3>{match.grant.title}</h3>
            {match.grant.sponsor && <p className="sponsor">{match.grant.sponsor}</p>}
            <p>{match.grant.description}</p>
            {match.grant.url && (
              <a href={match.grant.url} target="_blank" rel="noreferrer" className="match-link">
                View grant details
              </a>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
};

export default GrantMatchList;
