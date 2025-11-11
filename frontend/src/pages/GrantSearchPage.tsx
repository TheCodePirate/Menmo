import axios from 'axios';
import React from 'react';

import GrantSearchForm from '../components/GrantSearchForm';
import { GrantPayload } from '../types';

const GrantSearchPage: React.FC = () => {
  const handleIngest = async (grants: GrantPayload[]) => {
    await axios.post('/api/grants', grants);
  };

  return (
    <section className="page-shell content-card">
      <div className="section-heading">
        <span className="eyebrow">Knowledge ingestion</span>
        <h2>Keep Menmo aware of emerging opportunities</h2>
        <p>
          Paste the signal that matters—from new RFPs to internal grant notes—so the matching engine
          continuously recalibrates around your pipeline.
        </p>
      </div>
      <GrantSearchForm onIngest={handleIngest} />
    </section>
  );
};

export default GrantSearchPage;
