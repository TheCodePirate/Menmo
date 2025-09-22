export const azureB2cEnabled = process.env.NEXT_PUBLIC_AAD_CLIENT_ID !== undefined;

export const msalConfig = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AAD_CLIENT_ID || '00000000-0000-0000-0000-000000000000',
    authority:
      process.env.NEXT_PUBLIC_AAD_AUTHORITY ||
      `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AAD_TENANT_ID || 'common'}`,
    redirectUri: process.env.NEXT_PUBLIC_AAD_REDIRECT_URI || 'http://localhost:3000'
  },
  cache: {
    cacheLocation: 'localStorage' as const,
    storeAuthStateInCookie: false
  }
};

export const loginRequest = {
  scopes: [process.env.NEXT_PUBLIC_API_SCOPE || 'api://default/.default']
};
