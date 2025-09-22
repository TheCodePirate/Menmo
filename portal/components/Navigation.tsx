'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useIsAuthenticated, useMsal } from '@azure/msal-react';
import clsx from 'clsx';

const links = [
  { href: '/dashboard', label: 'Grant Dashboard' },
  { href: '/profile', label: 'Profile' }
];

export function Navigation() {
  const pathname = usePathname();
  const isAuthenticated = useIsAuthenticated();
  const { instance } = useMsal();

  const handleSignIn = () => {
    instance.loginRedirect();
  };

  const handleSignOut = () => {
    instance.logoutRedirect();
  };

  return (
    <header className="bg-white shadow-sm">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-xl font-semibold text-blue-700">
          Menmo Grants Portal
        </Link>
        <div className="flex items-center gap-6">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={clsx('text-sm font-medium text-slate-600 hover:text-slate-900', {
                'text-blue-700': pathname.startsWith(link.href)
              })}
            >
              {link.label}
            </Link>
          ))}
          {isAuthenticated ? (
            <button
              onClick={handleSignOut}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
            >
              Sign out
            </button>
          ) : (
            <button
              onClick={handleSignIn}
              className="rounded-md border border-blue-600 px-4 py-2 text-sm font-semibold text-blue-600 hover:bg-blue-50"
            >
              Sign in
            </button>
          )}
        </div>
      </nav>
    </header>
  );
}
