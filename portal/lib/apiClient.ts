import { AccountInfo, InteractionRequiredAuthError, IPublicClientApplication } from '@azure/msal-browser';
import { loginRequest } from './authConfig';

export interface Grant {
  id: string;
  title: string;
  summary: string;
  sourceUrl: string;
  deadline: string;
  eligibilityStatus: 'eligible' | 'ineligible' | 'unknown';
  matchConfidence?: number;
  citation?: string;
}

export interface GrantQueryParams {
  type: 'matched' | 'upcoming';
  status?: Grant['eligibilityStatus'];
  sort?: 'deadline' | 'confidence';
  search?: string;
}

async function getToken(instance: IPublicClientApplication, account: AccountInfo | null) {
  if (!account) {
    throw new Error('No active Azure AD account.');
  }

  try {
    const response = await instance.acquireTokenSilent({
      ...loginRequest,
      account
    });
    return response.accessToken;
  } catch (error) {
    if (error instanceof InteractionRequiredAuthError) {
      const response = await instance.acquireTokenPopup(loginRequest);
      return response.accessToken;
    }
    throw error;
  }
}

export async function callSecuredApi<T>(
  instance: IPublicClientApplication,
  account: AccountInfo | null,
  path: string,
  init?: RequestInit
): Promise<T> {
  const token = await getToken(instance, account);
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:7071/api';
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(init?.headers || {})
    }
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchGrants(
  instance: IPublicClientApplication,
  account: AccountInfo | null,
  params: GrantQueryParams
): Promise<Grant[]> {
  const query = new URLSearchParams({
    type: params.type,
    ...(params.status ? { status: params.status } : {}),
    ...(params.sort ? { sort: params.sort } : {}),
    ...(params.search ? { search: params.search } : {})
  });
  return callSecuredApi(instance, account, `/grants?${query.toString()}`);
}

export interface ProfilePayload {
  organizationName: string;
  contactName: string;
  contactEmail: string;
  focusAreas: string[];
  geography: string;
  fundingNeeds: string;
}

export async function upsertProfile(
  instance: IPublicClientApplication,
  account: AccountInfo | null,
  payload: ProfilePayload
) {
  return callSecuredApi(instance, account, `/profile`, {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function fetchProfile(
  instance: IPublicClientApplication,
  account: AccountInfo | null
): Promise<ProfilePayload> {
  return callSecuredApi(instance, account, `/profile`, {
    method: 'GET'
  });
}
