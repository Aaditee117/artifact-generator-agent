import axios from 'axios';
import { msalInstance, loginRequest } from '../config/msalConfig';

const api = axios.create({

  baseURL: 'http://localhost:5177/api',
  //'https://wpa-optistudio-eu2-dev-001-dpbgc7djhkhbcde5.eastus2-01.azurewebsites.net/api',
  
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const accounts = msalInstance.getAllAccounts();
        if (accounts.length > 0) {
          const msalResponse = await msalInstance.acquireTokenSilent({
            ...loginRequest,
            account: accounts[0]
          });
          
          if (msalResponse.idToken) {
            api.defaults.headers.common['Authorization'] = `Bearer ${msalResponse.idToken}`;
            originalRequest.headers['Authorization'] = `Bearer ${msalResponse.idToken}`;
            return api(originalRequest);
          }
        }
      } catch (msalError) {
        console.error('MSAL token refresh failed', msalError);
        const publicPaths = ['/login', '/register', '/verify-otp'];
        if (!publicPaths.includes(window.location.pathname)) {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;
