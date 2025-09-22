import type { Metadata } from 'next';
import { ReactNode } from 'react';
import './globals.css';
import { AuthProvider } from '@/components/AuthProvider';
import { Navigation } from '@/components/Navigation';

export const metadata: Metadata = {
  title: 'Menmo Grants Portal',
  description:
    'Secure workspace for authenticated nonprofits to manage profiles and review matched grant opportunities.'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-100 text-slate-900">
        <AuthProvider>
          <Navigation />
          <main className="mx-auto max-w-6xl px-6 py-10">
            <div className="rounded-3xl bg-white p-8 shadow-lg ring-1 ring-slate-200">
              {children}
            </div>
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
