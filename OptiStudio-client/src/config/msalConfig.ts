import { LogLevel, PublicClientApplication } from '@azure/msal-browser';
import type { Configuration } from '@azure/msal-browser';

// Get Azure AD configuration from environment variables or use defaults
const AZURE_CLIENT_ID = import.meta.env.VITE_AZURE_CLIENT_ID || 'd5752eb0-dfc0-4d3a-8a6a-907d6e1f7fdf';

// Multi-tenant authority options:
// - 'common': Any Microsoft account (personal + work/school)
// - 'organizations': Any Azure AD account (work/school only)
// - 'consumers': Microsoft personal accounts only
// - '{tenant-id}': Single tenant only
const AZURE_AUTHORITY = import.meta.env.VITE_AZURE_AUTHORITY || 'https://login.microsoftonline.com/common';

/**
 * MSAL configuration for Azure AD authentication.
 * Uses the app registration details from Azure portal.
 * Can be overridden via environment variables:
 * - VITE_AZURE_CLIENT_ID
 * - VITE_AZURE_AUTHORITY (default: common for multi-tenant)
 */
export const msalConfig: Configuration = {
  auth: {
    clientId: AZURE_CLIENT_ID,
    authority: AZURE_AUTHORITY,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'localStorage',
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) {
          return;
        }
        switch (level) {
          case LogLevel.Error:
            console.error('[MSAL]', message);
            return;
          case LogLevel.Info:
            console.info('[MSAL]', message);
            return;
          case LogLevel.Verbose:
            console.debug('[MSAL]', message);
            return;
          case LogLevel.Warning:
            console.warn('[MSAL]', message);
            return;
        }
      },
      logLevel: LogLevel.Info,
    },
  },
};

/**
 * Scopes for login - use basic OpenID scopes.
 * This gets an ID token that the backend can validate.
 */
export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
};

/**
 * Scopes for silent token acquisition
 */
export const tokenRequest = {
  scopes: ['openid', 'profile', 'email'],
};

/**
 * MSAL instance - create a single instance for the entire app.
 */
export const msalInstance = new PublicClientApplication(msalConfig);
