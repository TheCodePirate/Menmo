'use client';

import { Grant } from '@/lib/apiClient';
import { format, parseISO } from 'date-fns';

interface GrantCardProps {
  grant: Grant;
}

const statusToColor: Record<Grant['eligibilityStatus'], string> = {
  eligible: 'bg-emerald-100 text-emerald-700',
  ineligible: 'bg-rose-100 text-rose-700',
  unknown: 'bg-slate-100 text-slate-600'
};

export function GrantCard({ grant }: GrantCardProps) {
  const deadline = grant.deadline ? format(parseISO(grant.deadline), 'PPP') : 'TBD';
  return (
    <article className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{grant.title}</h3>
          <p className="mt-1 text-sm text-slate-600">{grant.summary}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusToColor[grant.eligibilityStatus]}`}>
          {grant.eligibilityStatus === 'eligible'
            ? 'Eligible'
            : grant.eligibilityStatus === 'ineligible'
              ? 'Ineligible'
              : 'Unknown'}
        </span>
      </div>
      <div className="flex flex-wrap items-center gap-4 text-sm text-slate-500">
        <span>
          <strong className="font-medium text-slate-700">Deadline:</strong> {deadline}
        </span>
        {grant.matchConfidence !== undefined && (
          <span>
            <strong className="font-medium text-slate-700">Match confidence:</strong> {grant.matchConfidence}%
          </span>
        )}
        {grant.citation && (
          <span className="italic">
            <strong className="font-medium text-slate-700">Source:</strong> {grant.citation}
          </span>
        )}
      </div>
      <div className="flex items-center justify-between">
        <a
          href={grant.sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="text-sm font-semibold text-blue-600 hover:text-blue-700"
        >
          View full details
        </a>
      </div>
    </article>
  );
}
