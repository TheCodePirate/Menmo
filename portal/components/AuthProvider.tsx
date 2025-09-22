'use client';

import { ReactNode, useMemo } from 'react';
import { MsalProvider, useMsal } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from '@/lib/authConfig';

interface AuthProviderProps {
  children: ReactNode;
}

const pca = new PublicClientApplication(msalConfig);

export function AuthProvider({ children }: AuthProviderProps) {
  return <MsalProvider instance={pca}>{children}</MsalProvider>;
}

export function useActiveAccount() {
  const { accounts } = useMsal();
  return useMemo(() => accounts[0] ?? null, [accounts]);
}
