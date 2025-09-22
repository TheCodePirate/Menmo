import React, { useState } from 'react';

import { UserProfilePayload } from '../types';

interface Props {
  onSubmit: (payload: UserProfilePayload) => Promise<void>;
}

const emptyForm: UserProfilePayload = {
  name: '',
  email: '',
  organization: '',
  focus_areas: '',
  goals: '',
};

const UserOnboardingForm: React.FC<Props> = ({ onSubmit }) => {
  const [form, setForm] = useState<UserProfilePayload>(emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setMessage(null);

    try {
      await onSubmit(form);
      setMessage('Profile saved!');
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
        <input name="name" value={form.name} onChange={handleChange} required />
      </label>
      <label>
        Email
        <input name="email" type="email" value={form.email} onChange={handleChange} required />
      </label>
      <label>
        Organization
        <input name="organization" value={form.organization} onChange={handleChange} />
      </label>
      <label>
        Focus Areas
        <input name="focus_areas" value={form.focus_areas} onChange={handleChange} />
      </label>
      <label>
        Goals
        <textarea name="goals" value={form.goals} onChange={handleChange} rows={4} />
      </label>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save profile'}
      </button>
      {message && <p className="status">{message}</p>}
    </form>
  );
};

export default UserOnboardingForm;
