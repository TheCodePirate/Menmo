import React from 'react';

import { QuickScanResult } from '../types';

interface Props {
  results: QuickScanResult[];
  isLoading?: boolean;
}

const QuickScanResults: React.FC<Props> = ({ results, isLoading }) => {
  if (isLoading) {
    return <p>Checking eligibility against stored grants...</p>;
  }

  if (!results.length) {
    return <p>No quick scan results yet. Provide profile details and run the scan.</p>;
  }

  return (
    <table className="quick-scan-results">
      <thead>
        <tr>
          <th>Grant</th>
          <th>Status</th>
          <th>Reasons</th>
          <th>Blockers</th>
        </tr>
      </thead>
      <tbody>
        {results.map((item) => (
          <tr key={item.grant_id}>
            <td>{item.grant_title}</td>
            <td>{item.status}</td>
            <td>
              <ul>
                {item.reasons.map((reason, index) => (
                  <li key={index}>{'text' in reason ? String(reason.text) : JSON.stringify(reason)}</li>
                ))}
              </ul>
            </td>
            <td>
              <ul>
                {item.blockers.map((blocker, index) => (
                  <li key={index}>{'text' in blocker ? String(blocker.text) : JSON.stringify(blocker)}</li>
                ))}
              </ul>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default QuickScanResults;
