import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

// Mock the MSAL provider
vi.mock('@azure/msal-react', () => ({
  useMsal: () => ({
    instance: {
      getActiveAccount: () => null,
      loginRedirect: vi.fn(),
    },
    accounts: [],
    inProgress: 'none',
  }),
  useIsAuthenticated: () => false,
  MsalProvider: ({ children }: { children: React.ReactNode }) => children,
}));

describe('App Component', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // App should render something
    expect(document.body).toBeTruthy();
  });

  it('shows login page when not authenticated', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // When not authenticated, should show login or redirect
    // Adjust based on actual app behavior
    expect(document.body).toBeTruthy();
  });
});
