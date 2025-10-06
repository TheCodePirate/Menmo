import React, { useState } from 'react';

import { FundingMatchPayload } from '../types';

interface Props {
  onSubmit: (payload: FundingMatchPayload) => Promise<void>;
  disabled?: boolean;
}

type FormState = Omit<FundingMatchPayload, 'capex' | 'opex' | 'co2_reduction' | 'top_k'> & {
  capex?: number | '';
  opex?: number | '';
  co2_reduction?: number | '';
  top_k?: number | '';
};

const initialState: FormState = {
  project_description: '',
  capex: undefined,
  opex: undefined,
  timeline: '',
  co2_reduction: undefined,
  partners: '',
  top_k: 5,
};

const FundingMatchForm: React.FC<Props> = ({ onSubmit, disabled }) => {
  const [form, setForm] = useState<FormState>(initialState);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTextChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
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
      [name]: value === '' ? '' : Number(value),
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const payload: FundingMatchPayload = {
        ...form,
        timeline: form.timeline?.trim() ? form.timeline : undefined,
        partners: form.partners?.trim() ? form.partners : undefined,
        capex: typeof form.capex === 'number' && !Number.isNaN(form.capex) ? form.capex : undefined,
        opex: typeof form.opex === 'number' && !Number.isNaN(form.opex) ? form.opex : undefined,
        co2_reduction:
          typeof form.co2_reduction === 'number' && !Number.isNaN(form.co2_reduction)
            ? form.co2_reduction
            : undefined,
        top_k: typeof form.top_k === 'number' && !Number.isNaN(form.top_k) ? form.top_k : undefined,
      };
      await onSubmit(payload);
    } catch (submitError) {
      setError('Unable to generate matches.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="funding-match-form">
      <label>
        Project description
        <textarea
          name="project_description"
          value={form.project_description ?? ''}
          onChange={handleTextChange}
          rows={4}
          required
          disabled={disabled}
        />
      </label>
      <div className="form-grid">
        <label>
          CapEx (in local currency)
          <input
            name="capex"
            type="number"
            min={0}
            step="any"
            value={form.capex ?? ''}
            onChange={handleNumberChange}
            disabled={disabled}
          />
        </label>
        <label>
          OpEx (annual)
          <input
            name="opex"
            type="number"
            min={0}
            step="any"
            value={form.opex ?? ''}
            onChange={handleNumberChange}
            disabled={disabled}
          />
        </label>
        <label>
          Timeline
          <input name="timeline" value={form.timeline ?? ''} onChange={handleTextChange} disabled={disabled} />
        </label>
        <label>
          Expected CO₂ reduction (tonnes)
          <input
            name="co2_reduction"
            type="number"
            min={0}
            step="any"
            value={form.co2_reduction ?? ''}
            onChange={handleNumberChange}
            disabled={disabled}
          />
        </label>
        <label>
          Partners
          <input name="partners" value={form.partners ?? ''} onChange={handleTextChange} disabled={disabled} />
        </label>
        <label>
          Number of matches
          <input
            name="top_k"
            type="number"
            min={1}
            max={10}
            value={form.top_k ?? 5}
            onChange={handleNumberChange}
            disabled={disabled}
          />
        </label>
      </div>
      <button type="submit" disabled={disabled || isSubmitting}>
        {isSubmitting ? 'Generating...' : 'Generate matches'}
      </button>
      {error && <p className="status error">{error}</p>}
    </form>
  );
};

export default FundingMatchForm;
