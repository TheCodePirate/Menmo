import axios from 'axios';
import React, { useCallback, useEffect, useState } from 'react';

import FundingMatchForm from '../components/FundingMatchForm';
import GrantMatchList from '../components/GrantMatchList';
import QuickScanForm from '../components/QuickScanForm';
import QuickScanResults from '../components/QuickScanResults';
import {
  FundingMatchPayload,
  MatchResult,
  QuickScanPayload,
  QuickScanResult,
  UserProfile,
} from '../types';

interface Props {
  userId: number | null;
}

const MatchesPage: React.FC<Props> = ({ userId }) => {
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [quickScanResults, setQuickScanResults] = useState<QuickScanResult[]>([]);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);
  const [isLoadingQuickScan, setIsLoadingQuickScan] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);

  const resetStateForUser = useCallback(() => {
    setMatches([]);
    setQuickScanResults([]);
    setMessage(null);
    setProfile(null);
  }, []);

  const fetchMatches = useCallback(async () => {
    if (!userId) {
      resetStateForUser();
      return;
    }
    setIsLoadingMatches(true);
    try {
      const response = await axios.get(`/api/matches/${userId}`);
      setMatches(response.data);
    } catch (error) {
      setMatches([]);
    } finally {
      setIsLoadingMatches(false);
    }
  }, [resetStateForUser, userId]);

  const fetchProfile = useCallback(async () => {
    if (!userId) {
      setProfile(null);
      return;
    }
    try {
      const response = await axios.get(`/api/users/${userId}`);
      setProfile(response.data);
    } catch (error) {
      setProfile(null);
    }
  }, [userId]);

  useEffect(() => {
    if (!userId) {
      resetStateForUser();
      return;
    }
    fetchMatches();
    fetchProfile();
  }, [fetchMatches, fetchProfile, resetStateForUser, userId]);

  const handleQuickScan = async (payload: QuickScanPayload) => {
    if (!userId) {
      return;
    }
    setIsLoadingQuickScan(true);
    setMessage(null);
    try {
      const response = await axios.post('/api/journey/quick-scan', {
        ...payload,
        user_id: userId,
      });
      setQuickScanResults(response.data);
      setMessage('Quick scan completed. Review blockers before moving forward.');
    } catch (error) {
      setMessage('Unable to run the quick scan. Please adjust your inputs and try again.');
    } finally {
      setIsLoadingQuickScan(false);
    }
  };

  const handleFundingMatch = async (payload: FundingMatchPayload) => {
    if (!userId) {
      return;
    }
    setIsLoadingMatches(true);
    setMessage(null);
    try {
      const response = await axios.post('/api/journey/funding-match', {
        ...payload,
        user_id: userId,
      });
      setMatches(response.data);
      setMessage('Matches updated using your latest project profile.');
    } catch (error) {
      setMessage('Unable to generate matches. Double-check the project details and try again.');
    } finally {
      setIsLoadingMatches(false);
    }
  };

  if (!userId) {
    return <p>Create a user profile to unlock personalized matches.</p>;
  }

  return (
    <section className="matches-page">
      <h2>Recommended Matches</h2>
      <p>
        Run a quick eligibility scan to understand blockers, then enrich your project brief to
        generate personalised funding matches.
      </p>
      {profile && (
        <div className="profile-summary">
          <h4>Active profile</h4>
          <ul>
            <li>
              <strong>Organization:</strong> {profile.organization || '—'}
            </li>
            <li>
              <strong>Industry:</strong> {profile.industry || '—'}
            </li>
            <li>
              <strong>Location:</strong> {profile.location || '—'}
            </li>
            <li>
              <strong>Project type:</strong> {profile.project_type || '—'}
            </li>
          </ul>
        </div>
      )}
      {message && <p className="status">{message}</p>}

      <article>
        <h3>1. Quick eligibility scan</h3>
        <QuickScanForm
          onSubmit={handleQuickScan}
          disabled={isLoadingMatches}
          initialValues={
            profile
              ? {
                  industry: profile.industry,
                  entity_type: profile.entity_type,
                  location: profile.location,
                  company_size: profile.company_size,
                  project_type: profile.project_type,
                  budget_min: profile.budget_min,
                  budget_max: profile.budget_max,
                }
              : null
          }
        />
        <QuickScanResults results={quickScanResults} isLoading={isLoadingQuickScan} />
      </article>

      <article>
        <h3>2. Generate funding matches</h3>
        <FundingMatchForm onSubmit={handleFundingMatch} disabled={isLoadingQuickScan} />
      </article>

      <article>
        <h3>3. Review recommendations</h3>
        <GrantMatchList matches={matches} isLoading={isLoadingMatches} />
      </article>
    </section>
  );
};

export default MatchesPage;
