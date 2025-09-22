import axios from 'axios';
import React from 'react';

import GrantSearchForm from '../components/GrantSearchForm';
import { GrantPayload } from '../types';

const GrantSearchPage: React.FC = () => {
  const handleIngest = async (grants: GrantPayload[]) => {
    await axios.post('/api/grants', grants);
  };

  return (
    <section>
      <h2>Ingest new grants</h2>
      <p>Paste relevant information about opportunities to keep the recommendation engine up to date.</p>
      <GrantSearchForm onIngest={handleIngest} />
    </section>
  );
};

export default GrantSearchPage;
