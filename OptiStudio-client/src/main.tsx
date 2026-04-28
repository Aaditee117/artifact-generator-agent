import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { MsalProvider } from '@azure/msal-react'
import { msalInstance } from './config/msalConfig'
import './index.css'
import App from './App.tsx'

// Render the app with MSAL Provider
const root = createRoot(document.getElementById('root')!);

// Initialize MSAL and render
msalInstance.initialize().then(() => {
  // Handle redirect promise (for when returning from Azure AD login)
  msalInstance.handleRedirectPromise()
    .then((response) => {
      if (response) {
        console.log('MSAL: Logged in as', response.account?.username);
      }
    })
    .catch((error) => {
      console.error('MSAL redirect error:', error);
    });

  // Render the app
  root.render(
    <StrictMode>
      <MsalProvider instance={msalInstance}>
        <App />
      </MsalProvider>
    </StrictMode>,
  );
}).catch((error) => {
  console.error('MSAL initialization error:', error);
  // Render app anyway to show error state
  root.render(
    <StrictMode>
      <MsalProvider instance={msalInstance}>
        <App />
      </MsalProvider>
    </StrictMode>,
  );
});
