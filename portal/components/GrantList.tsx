'use client';

import { useEffect, useState } from 'react';
import useSWR from 'swr';
import { fetchGrants, GrantQueryParams } from '@/lib/apiClient';
import { useActiveAccount } from './AuthProvider';
import { useMsal } from '@azure/msal-react';
import { GrantCard } from './GrantCard';
import { GrantFilters } from './GrantFilters';

interface GrantListProps {
  initialType: GrantQueryParams['type'];
}

const defaultFilters: GrantQueryParams = {
  type: 'matched',
  sort: 'deadline'
};

export function GrantList({ initialType }: GrantListProps) {
  const [filters, setFilters] = useState<GrantQueryParams>({ ...defaultFilters, type: initialType });
  const account = useActiveAccount();
  const { instance } = useMsal();
  const { data, error, isLoading, mutate } = useSWR(
    account ? ['grants', filters, account.homeAccountId] : null,
    () => fetchGrants(instance, account, filters)
  );

  useEffect(() => {
    setFilters((prev) => ({ ...prev, type: initialType }));
  }, [initialType]);

  return (
    <section className="flex flex-col gap-6">
      <GrantFilters
        params={filters}
        onChange={(updater) =>
          setFilters((prev) => (typeof updater === 'function' ? updater(prev) : updater))
        }
      />
      <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-600">
        Filtering and sorting are applied server-side via the Azure Functions grant matching API.
        Use the controls above to refine matched and upcoming opportunities.
        <button
          className="ml-3 text-blue-600 hover:text-blue-700"
          onClick={() => mutate()}
          type="button"
        >
          Refresh data
        </button>
      </div>
      {isLoading && <p className="text-sm text-slate-500">Loading grants…</p>}
      {error && <p className="text-sm text-rose-600">Unable to load grants: {error.message}</p>}
      <div className="grid gap-4 md:grid-cols-2">
        {data?.map((grant) => (
          <GrantCard key={grant.id} grant={grant} />
        ))}
      </div>
      {!isLoading && data?.length === 0 && (
        <p className="text-sm text-slate-500">No grants match the current filters.</p>
      )}
    </section>
  );
}
