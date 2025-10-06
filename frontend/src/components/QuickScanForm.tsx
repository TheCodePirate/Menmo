import React, { useState } from 'react';

import { QuickScanPayload } from '../types';

interface Props {
  onSubmit: (payload: QuickScanPayload) => Promise<void>;
  disabled?: boolean;
  initialValues?: QuickScanPayload | null;
}

const initialState: QuickScanPayload = {
  industry: '',
  entity_type: '',
  location: '',
  company_size: '',
  project_type: '',
  budget_min: undefined,
  budget_max: undefined,
};

const QuickScanForm: React.FC<Props> = ({ onSubmit, disabled, initialValues }) => {
  const baseValues = initialValues ?? {};
  const [form, setForm] = useState<QuickScanPayload>({ ...initialState, ...baseValues });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    const defaults = initialValues ?? {};
    setForm({ ...initialState, ...defaults });
  }, [initialValues]);

  const handleTextChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: value === '' ? undefined : value,
    }));
  };

  const handleNumberChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: value === '' ? undefined : Number(value),
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(form);
    } catch (submitError) {
      setError('Unable to run the quick scan.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="quick-scan-form">
      <div className="form-grid">
        <label>
          Industry
          <input name="industry" value={form.industry ?? ''} onChange={handleTextChange} disabled={disabled} />
        </label>
        <label>
          Entity type
          <input name="entity_type" value={form.entity_type ?? ''} onChange={handleTextChange} disabled={disabled} />
        </label>
        <label>
          Location
          <input name="location" value={form.location ?? ''} onChange={handleTextChange} disabled={disabled} />
        </label>
        <label>
          Company size
          <input name="company_size" value={form.company_size ?? ''} onChange={handleTextChange} disabled={disabled} />
        </label>
        <label>
          Project type
          <input name="project_type" value={form.project_type ?? ''} onChange={handleTextChange} disabled={disabled} />
        </label>
        <label>
          Budget minimum
          <input
            name="budget_min"
            type="number"
            min={0}
            step="any"
            value={form.budget_min ?? ''}
            onChange={handleNumberChange}
            disabled={disabled}
          />
        </label>
        <label>
          Budget maximum
          <input
            name="budget_max"
            type="number"
            min={0}
            step="any"
            value={form.budget_max ?? ''}
            onChange={handleNumberChange}
            disabled={disabled}
          />
        </label>
      </div>
      <button type="submit" disabled={disabled || isSubmitting}>
        {isSubmitting ? 'Scanning...' : 'Run quick scan'}
      </button>
      {error && <p className="status error">{error}</p>}
    </form>
  );
};

export default QuickScanForm;
