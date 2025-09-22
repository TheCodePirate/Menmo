import React, { useState } from 'react';

import { GrantPayload } from '../types';

interface Props {
  onIngest: (grants: GrantPayload[]) => Promise<void>;
}

const defaultGrant: GrantPayload = {
  title: '',
  description: '',
  sponsor: '',
  deadline: '',
  url: '',
};

const GrantSearchForm: React.FC<Props> = ({ onIngest }) => {
  const [grant, setGrant] = useState<GrantPayload>(defaultGrant);
  const [message, setMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setGrant((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setMessage(null);
    try {
      await onIngest([{ ...grant }]);
      setMessage('Grant ingested!');
      setGrant(defaultGrant);
    } catch (error) {
      setMessage('Unable to ingest grant.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="grant-ingest-form">
      <label>
        Title
        <input name="title" value={grant.title} onChange={handleChange} required />
      </label>
      <label>
        Description
        <textarea name="description" value={grant.description} onChange={handleChange} rows={4} required />
      </label>
      <label>
        Sponsor
        <input name="sponsor" value={grant.sponsor} onChange={handleChange} />
      </label>
      <label>
        Deadline
        <input name="deadline" value={grant.deadline} onChange={handleChange} />
      </label>
      <label>
        URL
        <input name="url" value={grant.url} onChange={handleChange} />
      </label>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Ingesting...' : 'Ingest grant'}
      </button>
      {message && <p className="status">{message}</p>}
    </form>
  );
};

export default GrantSearchForm;
