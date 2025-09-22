import { GrantList } from '@/components/GrantList';
import { Suspense } from 'react';
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-10">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold text-slate-900">Grant intelligence</h1>
        <p className="text-base text-slate-600">
          Explore personalized funding opportunities curated by Menmo.
          The matched view prioritizes grants aligned to your profile while the upcoming view shows deadlines on the horizon.
        </p>
      </header>
      <AuthenticatedTemplate>
        <Suspense fallback={<p className="text-sm text-slate-500">Loading grant dashboards…</p>}>
          <div className="flex flex-col gap-12">
            <section className="flex flex-col gap-4">
              <div>
                <h2 className="text-2xl font-semibold text-slate-900">Matched grants</h2>
                <p className="text-sm text-slate-600">
                  Prioritized based on similarity to your saved focus areas, funding needs, and historical awards.
                </p>
              </div>
              <GrantList initialType="matched" />
            </section>
            <section className="flex flex-col gap-4">
              <div>
                <h2 className="text-2xl font-semibold text-slate-900">Upcoming deadlines</h2>
                <p className="text-sm text-slate-600">
                  Keep track of relevant funding windows closing soon so you can plan submissions with confidence.
                </p>
              </div>
              <GrantList initialType="upcoming" />
            </section>
          </div>
        </Suspense>
      </AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <div className="rounded-2xl border border-blue-100 bg-blue-50 p-6 text-center text-slate-700">
          <p className="text-base font-medium">Sign in with Azure AD to view recommended grants.</p>
        </div>
      </UnauthenticatedTemplate>
    </div>
  );
}
