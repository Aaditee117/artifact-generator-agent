import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { InteractionStatus } from '@azure/msal-browser';
import { loginRequest } from '../config/msalConfig';
import api from '../services/api';

interface User {
  id: string;
  name: string;
  email: string;
  isEmailVerified: boolean;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (...roles: string[]) => boolean;
  getAccessToken: () => Promise<string | null>;
  register: (name: string, email: string, password: string, confirmPassword: string) => Promise<{ success: boolean; message: string }>; 
  verifyOtp: (email: string, otp: string) => Promise<{ success: boolean; message: string }>;
  resendOtp: (email: string) => Promise<{ success: boolean; message: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Get token for API calls - use ID token since we're using basic scopes
  const getAccessToken = useCallback(async (): Promise<string | null> => {
    if (accounts.length === 0) {
      return null;
    }

    try {
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account: accounts[0],
      });
      // Use ID token since access token is for Graph API
      // ID token contains our user's identity claims
      console.log('[Auth] Token acquired, using idToken');
      return response.idToken;
    } catch (error) {
      console.error('Failed to acquire token silently:', error);
      // If silent acquisition fails, try interactive
      try {
        const response = await instance.acquireTokenPopup(loginRequest);
        return response.idToken;
      } catch (interactiveError) {
        console.error('Failed to acquire token interactively:', interactiveError);
        return null;
      }
    }
  }, [instance, accounts]);

  // Fetch user info from backend API
  const fetchUserInfo = useCallback(async () => {
    try {
      const token = await getAccessToken();
      console.log('[Auth] Got token:', token ? 'Yes (length: ' + token.length + ')' : 'No');

      if (!token) {
        console.log('[Auth] No token, setting user to null');
        setUser(null);
        return;
      }

      // Set the token in axios headers for API calls
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      console.log('[Auth] Calling /auth/me...');
      const response = await api.get('/auth/me');
      console.log('[Auth] Response status:', response.status);
      console.log('[Auth] Response data:', response.data);

      if (response.data.success && response.data.user) {
        console.log('[Auth] Setting user from API:', response.data.user);
        console.log('[Auth] User created/found in database with role:', response.data.user.role);
        setUser(response.data.user);
      } else {
        console.warn('[Auth] API response not successful:', response.data.message);
        setUser(null);
      }
    } catch (error: any) {
      console.error('[Auth] Failed to fetch user info:', error);
      console.error('[Auth] Error response:', error.response?.data);
      console.error('[Auth] Error status:', error.response?.status);
      // Don't fall back to hardcoded role — user must re-login to get proper DB role
      setUser(null);
    }
  }, [getAccessToken]);

  // Handle authentication state changes
  useEffect(() => {
    if (inProgress === InteractionStatus.None) {
      if (isAuthenticated && accounts.length > 0) {
        fetchUserInfo().finally(() => setLoading(false));
      } else {
        setUser(null);
        setLoading(false);
      }
    }
  }, [isAuthenticated, accounts, inProgress, fetchUserInfo]);

  // Login using MSAL redirect
  const login = async () => {
    // Prevent multiple login attempts if already authenticated
    if (isAuthenticated && accounts.length > 0) {
      console.log('[Auth] Already authenticated, skipping loginRedirect');
      return;
    }
    try {
      await instance.loginRedirect(loginRequest);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  // Logout using MSAL
  const logout = async () => {
    try {
      // Clear axios auth header
      delete api.defaults.headers.common['Authorization'];

      // Call backend logout endpoint (optional cleanup)
      try {
        const token = await getAccessToken();
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          await api.post('/auth/logout');
        }
      } catch {
        // Ignore errors from backend logout
      }

      // Clear local state
      setUser(null);

      // Perform MSAL logout
      await instance.logoutRedirect({
        postLogoutRedirectUri: '/',
      });
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  };

  const hasRole = (...roles: string[]) => {
    if (!user) return false;
    return roles.some(r => r.toLowerCase() === user.role.toLowerCase());
  };

  // Placeholder implementations (replace with real API calls)
  const register = async (name: string, email: string, password: string, confirmPassword: string) => {
    try {
      const response = await api.post('/auth/register', { name, email, password, confirmPassword });
      return { success: response.data.success, message: response.data.message };
    } catch (err: any) {
      return { success: false, message: err.response?.data?.message || 'Registration failed.' };
    }
  };

  const verifyOtp = async (email: string, otp: string) => {
    try {
      const response = await api.post('/auth/verify-otp', { email, otp });
      return { success: response.data.success, message: response.data.message };
    } catch (err: any) {
      return { success: false, message: err.response?.data?.message || 'OTP verification failed.' };
    }
  };

  const resendOtp = async (email: string) => {
    try {
      const response = await api.post('/auth/resend-otp', { email });
      return { success: response.data.success, message: response.data.message };
    } catch (err: any) {
      return { success: false, message: err.response?.data?.message || 'Failed to resend OTP.' };
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasRole, getAccessToken, register, verifyOtp, resendOtp }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
