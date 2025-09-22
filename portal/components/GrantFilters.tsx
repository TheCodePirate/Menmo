'use client';

import { Dispatch, SetStateAction } from 'react';
import { GrantQueryParams } from '@/lib/apiClient';

interface GrantFiltersProps {
  params: GrantQueryParams;
  onChange: Dispatch<SetStateAction<GrantQueryParams>>;
}

export function GrantFilters({ params, onChange }: GrantFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Search</label>
        <input
          value={params.search ?? ''}
          onChange={(event) => onChange((prev) => ({ ...prev, search: event.target.value }))}
          className="mt-1 w-64 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          placeholder="Keywords"
        />
      </div>
      <div className="flex flex-col">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Eligibility</label>
        <select
          value={params.status ?? ''}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, status: event.target.value ? (event.target.value as GrantQueryParams['status']) : undefined }))
          }
          className="mt-1 w-48 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        >
          <option value="">All statuses</option>
          <option value="eligible">Eligible</option>
          <option value="ineligible">Ineligible</option>
          <option value="unknown">Unknown</option>
        </select>
      </div>
      <div className="flex flex-col">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Sort by</label>
        <select
          value={params.sort ?? 'deadline'}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, sort: event.target.value as GrantQueryParams['sort'] }))
          }
          className="mt-1 w-48 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        >
          <option value="deadline">Deadline</option>
          <option value="confidence">Match confidence</option>
        </select>
      </div>
      <div className="flex flex-col">
        <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">View</label>
        <div className="mt-1 flex rounded-md border border-slate-300 bg-slate-50 p-1 text-sm">
          <button
            className={`flex-1 rounded-md px-3 py-2 ${params.type === 'matched' ? 'bg-white font-semibold text-blue-600 shadow-sm' : 'text-slate-600'}`}
            onClick={() => onChange((prev) => ({ ...prev, type: 'matched' }))}
          >
            Matched
          </button>
          <button
            className={`flex-1 rounded-md px-3 py-2 ${params.type === 'upcoming' ? 'bg-white font-semibold text-blue-600 shadow-sm' : 'text-slate-600'}`}
            onClick={() => onChange((prev) => ({ ...prev, type: 'upcoming' }))}
          >
            Upcoming
          </button>
        </div>
      </div>
    </div>
  );
}
