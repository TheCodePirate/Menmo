# Menmo

menmo.ai

## Portal front-end

The `portal/` directory contains a Next.js application that provides an authenticated experience for nonprofit partners to
manage their organization profile and explore grant recommendations surfaced by Menmo's Azure Functions APIs.

### Key capabilities

- **Azure Active Directory authentication** using MSAL so that only authorized users can access the portal.
- **Profile management** forms that update your organization's focus areas, geography, and funding needs via the secured
  profile endpoint.
- **Grant dashboards** for matched and upcoming opportunities with filtering, sorting, eligibility status, deadline
  awareness, and citation callouts.

## Local development

### Prerequisites

- Node.js 18+ and npm
- Access to the Azure Active Directory app registration that secures your Azure Functions APIs

### Install dependencies

```bash
cd portal
npm install
```

### Configure environment

Create a `.env.local` file inside `portal/` to expose the values that MSAL and the API client need:

```ini
NEXT_PUBLIC_AAD_CLIENT_ID=<azure-ad-app-client-id>
NEXT_PUBLIC_AAD_TENANT_ID=<azure-ad-tenant-id>
# Optional override if you use a custom authority such as B2C policies
NEXT_PUBLIC_AAD_AUTHORITY=https://login.microsoftonline.com/<tenant-or-policy>
NEXT_PUBLIC_AAD_REDIRECT_URI=http://localhost:3000
NEXT_PUBLIC_API_SCOPE=api://<functions-app-id>/user_impersonation
NEXT_PUBLIC_API_BASE_URL=https://<functions-app>.azurewebsites.net/api
```

If you are protecting the Azure Functions with role assignments, make sure the signed-in account has the proper role and
that the exposed API permissions are granted to the portal app registration.

### Run the development server

```bash
npm run dev
```

Navigate to `http://localhost:3000` and complete the Azure AD sign-in to load your personalized dashboards. The portal
includes two main authenticated routes:

- `/dashboard` – Fetches matched and upcoming grants by calling the `/grants` Azure Function with the acquired access token
  and applies your selected filters (search, eligibility, sorting).
- `/profile` – Loads and submits organization information by calling the `/profile` Azure Function.

## Deployment guidance

The portal is a static Next.js application that can be deployed to Azure Static Web Apps or hosted behind an App Service
with Next.js server rendering support.

### Azure Static Web Apps

1. Create a Static Web App resource and connect it to this repository.
2. Use the build preset `Next.js` with the app location `portal`, output location `.next`, and install command `npm install`.
3. Add the environment variables from `.env.local` to the Static Web App configuration (Azure Portal > Configuration >
   Application settings).
4. Ensure the Azure Functions APIs are configured as an integrated or linked backend so that the portal can reach the
   secured endpoints.

### Azure App Service

1. Provision an App Service instance running Linux with Node.js 18 or greater.
2. Deploy the built application (`npm run build`) using your preferred method (GitHub Actions, `az webapp deploy`, etc.).
3. Configure the same environment variables under App Service > Settings > Configuration.
4. If your Azure Functions are in the same virtual network, enable VNet integration or expose them publicly with proper
   authentication to allow the portal to reach them.

After deployment, update the `NEXT_PUBLIC_AAD_REDIRECT_URI` in your environment to the production hostname and add the
redirect URI to your Azure AD app registration.
