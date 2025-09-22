'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { useActiveAccount } from './AuthProvider';
import useSWR from 'swr';
import { fetchProfile, ProfilePayload, upsertProfile } from '@/lib/apiClient';

const defaultProfile: ProfilePayload = {
  organizationName: '',
  contactName: '',
  contactEmail: '',
  focusAreas: [],
  geography: '',
  fundingNeeds: ''
};

export function ProfileForm() {
  const { instance } = useMsal();
  const account = useActiveAccount();
  const { data, error, isLoading, mutate } = useSWR(account ? ['profile', account.homeAccountId] : null, () =>
    fetchProfile(instance, account)
  );
  const [formState, setFormState] = useState<ProfilePayload>(defaultProfile);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    if (data) {
      setFormState({ ...defaultProfile, ...data });
    }
  }, [data]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await upsertProfile(instance, account, {
        ...formState,
        focusAreas: formState.focusAreas.filter(Boolean)
      });
      setStatus('Profile saved successfully.');
      mutate();
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Failed to save profile');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <div className="grid gap-6 md:grid-cols-2">
        <Field
          label="Organization name"
          value={formState.organizationName}
          onChange={(value) => setFormState((prev) => ({ ...prev, organizationName: value }))}
        />
        <Field
          label="Geography"
          value={formState.geography}
          onChange={(value) => setFormState((prev) => ({ ...prev, geography: value }))}
        />
        <Field
          label="Primary contact"
          value={formState.contactName}
          onChange={(value) => setFormState((prev) => ({ ...prev, contactName: value }))}
        />
        <Field
          label="Contact email"
          type="email"
          value={formState.contactEmail}
          onChange={(value) => setFormState((prev) => ({ ...prev, contactEmail: value }))}
        />
      </div>
      <TagInput
        label="Focus areas"
        values={formState.focusAreas}
        onChange={(values) => setFormState((prev) => ({ ...prev, focusAreas: values }))}
      />
      <div>
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Funding needs</label>
        <textarea
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          rows={4}
          value={formState.fundingNeeds}
          onChange={(event) => setFormState((prev) => ({ ...prev, fundingNeeds: event.target.value }))}
        />
      </div>
      {status && <p className="text-sm text-blue-600">{status}</p>}
      {error && <p className="text-sm text-rose-600">Unable to load profile: {error.message}</p>}
      {isLoading && <p className="text-sm text-slate-500">Loading profile…</p>}
      <div className="flex justify-end">
        <button
          type="submit"
          className="rounded-md bg-blue-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
        >
          Save profile
        </button>
      </div>
    </form>
  );
}

interface FieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}

function Field({ label, value, onChange, type = 'text' }: FieldProps) {
  return (
    <div className="flex flex-col">
      <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      />
    </div>
  );
}

interface TagInputProps {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
}

function TagInput({ label, values, onChange }: TagInputProps) {
  const [inputValue, setInputValue] = useState('');

  const addTag = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !values.includes(trimmed)) {
      onChange([...values, trimmed]);
    }
    setInputValue('');
  };

  const removeTag = (tag: string) => {
    onChange(values.filter((value) => value !== tag));
  };

  return (
    <div className="flex flex-col">
      <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</label>
      <div className="mt-1 flex flex-wrap gap-2">
        {values.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700"
          >
            {tag}
            <button type="button" onClick={() => removeTag(tag)} className="text-blue-500 hover:text-blue-700">
              ×
            </button>
          </span>
        ))}
        <div className="flex items-center gap-2">
          <input
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault();
                addTag();
              }
            }}
            className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            placeholder="Add focus area"
          />
          <button
            type="button"
            onClick={addTag}
            className="rounded-md border border-blue-600 px-3 py-2 text-xs font-semibold text-blue-600 hover:bg-blue-50"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
}
