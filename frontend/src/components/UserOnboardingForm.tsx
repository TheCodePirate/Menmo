import React, { useState } from 'react';

import { UserProfilePayload } from '../types';

interface Props {
  onSubmit: (payload: UserProfilePayload) => Promise<void>;
}

type FormState = Omit<UserProfilePayload, 'budget_min' | 'budget_max'> & {
  budget_min?: number | '';
  budget_max?: number | '';
};

const initialForm: FormState = {
  name: '',
  email: '',
  organization: '',
  focus_areas: '',
  goals: '',
  industry: '',
  entity_type: '',
  location: '',
  company_size: '',
  project_type: '',
  budget_min: '',
  budget_max: '',
};

const UserOnboardingForm: React.FC<Props> = ({ onSubmit }) => {
  const [form, setForm] = useState<FormState>(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleTextChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
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
    setMessage(null);

    try {
      const payload: UserProfilePayload = {
        ...form,
        name: form.name.trim(),
        email: form.email.trim(),
        organization: form.organization?.trim() ? form.organization.trim() : undefined,
        focus_areas: form.focus_areas?.trim() ? form.focus_areas.trim() : undefined,
        goals: form.goals?.trim() ? form.goals.trim() : undefined,
        industry: form.industry?.trim() ? form.industry.trim() : undefined,
        entity_type: form.entity_type?.trim() ? form.entity_type.trim() : undefined,
        location: form.location?.trim() ? form.location.trim() : undefined,
        company_size: form.company_size?.trim() ? form.company_size.trim() : undefined,
        project_type: form.project_type?.trim() ? form.project_type.trim() : undefined,
        budget_min:
          typeof form.budget_min === 'number' && !Number.isNaN(form.budget_min)
            ? form.budget_min
            : undefined,
        budget_max:
          typeof form.budget_max === 'number' && !Number.isNaN(form.budget_max)
            ? form.budget_max
            : undefined,
      };
      await onSubmit(payload);
      setMessage('Profile saved!');
      setForm(initialForm);
    } catch (error) {
      setMessage('Unable to save profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="onboarding-form">
      <label>
        Name
        <input name="name" value={form.name ?? ''} onChange={handleTextChange} required />
      </label>
      <label>
        Email
        <input
          name="email"
          type="email"
          value={form.email ?? ''}
          onChange={handleTextChange}
          required
        />
      </label>
      <label>
        Organization
        <input
          name="organization"
          value={form.organization ?? ''}
          onChange={handleTextChange}
        />
      </label>
      <label>
        Focus Areas
        <input
          name="focus_areas"
          value={form.focus_areas ?? ''}
          onChange={handleTextChange}
        />
      </label>
      <label>
        Goals
        <textarea
          name="goals"
          value={form.goals ?? ''}
          onChange={handleTextChange}
          rows={4}
        />
      </label>
      <fieldset>
        <legend>Eligibility quick scan inputs</legend>
        <label>
          Industry
          <input name="industry" value={form.industry ?? ''} onChange={handleTextChange} />
        </label>
        <label>
          Entity type
          <input name="entity_type" value={form.entity_type ?? ''} onChange={handleTextChange} />
        </label>
        <label>
          Location
          <input name="location" value={form.location ?? ''} onChange={handleTextChange} />
        </label>
        <label>
          Company size
          <input
            name="company_size"
            value={form.company_size ?? ''}
            onChange={handleTextChange}
          />
        </label>
        <label>
          Project type
          <input
            name="project_type"
            value={form.project_type ?? ''}
            onChange={handleTextChange}
          />
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
          />
        </label>
      </fieldset>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save profile'}
      </button>
      {message && <p className="status">{message}</p>}
    </form>
  );
};

export default UserOnboardingForm;
