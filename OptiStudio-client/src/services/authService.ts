import api from './api';

export interface AuthResponse {
  success: boolean;
  message: string;
  accessToken?: string;
  refreshToken?: string;
  accessTokenExpiry?: string;
  user?: {
    id: string;
    name: string;
    email: string;
    isEmailVerified: boolean;
    role: string;
  };
}

export interface UserListResponse {
  success: boolean;
  message: string;
  users: {
    id: string;
    name: string;
    email: string;
    isEmailVerified: boolean;
    role: string;
  }[];
}

export const authService = {
  register: (name: string, email: string, password: string, confirmPassword: string) =>
    api.post<AuthResponse>('/auth/register', { name, email, password, confirmPassword }),

  verifyOtp: (email: string, otpCode: string) =>
    api.post<AuthResponse>('/auth/verify-otp', { email, otpCode }),

  login: (email: string, password: string) =>
    api.post<AuthResponse>('/auth/login', { email, password }),

  logout: () => api.post<AuthResponse>('/auth/logout'),

  refreshToken: () => api.post<AuthResponse>('/auth/refresh-token'),

  getCurrentUser: () => api.get<AuthResponse>('/auth/me'),

  resendOtp: (email: string) =>
    api.post<AuthResponse>('/auth/resend-otp', { email }),
};

export const adminService = {
  getAllUsers: (search?: string) =>
    api.get<UserListResponse>('/admin/users', { params: search ? { search } : undefined }),

  updateUserRole: (userId: string, role: string) =>
    api.put<AuthResponse>(`/admin/users/${userId}/role`, { role }),
};
