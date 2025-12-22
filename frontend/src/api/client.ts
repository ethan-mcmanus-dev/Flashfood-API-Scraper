/**
 * API client for communicating with the FastAPI backend.
 *
 * Handles authentication, request/response formatting, and error handling.
 */

import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';
import type {
  User,
  Store,
  Product,
  ProductWithHistory,
  UserPreference,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

/**
 * Axios instance configured for API requests.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_V1_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Add authentication token to requests if available.
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Handle authentication errors globally.
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Authentication API endpoints.
 */
export const authApi = {
  /**
   * Register a new user account.
   */
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * Login with email and password.
   */
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await apiClient.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store token in localStorage
    localStorage.setItem('access_token', response.data.access_token);

    return response.data;
  },

  /**
   * Get current authenticated user profile.
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Logout by clearing stored token.
   */
  logout: (): void => {
    localStorage.removeItem('access_token');
  },
};

/**
 * Store API endpoints.
 */
export const storeApi = {
  /**
   * List all stores with optional filters.
   */
  listStores: async (params?: {
    city?: string;
    max_distance_km?: number;
  }): Promise<Store[]> => {
    const response = await apiClient.get<Store[]>('/stores/', { params });
    return response.data;
  },

  /**
   * Get a specific store by ID.
   */
  getStore: async (storeId: number): Promise<Store> => {
    const response = await apiClient.get<Store>(`/stores/${storeId}`);
    return response.data;
  },
};

/**
 * Product (deals) API endpoints.
 */
export const productApi = {
  /**
   * List all products with optional filters.
   */
  listProducts: async (params?: {
    city?: string;
    store_id?: number;
    category?: string;
    min_discount?: number;
    search?: string;
    limit?: number;
    use_preferences?: boolean;
  }): Promise<Product[]> => {
    const response = await apiClient.get<Product[]>('/products/', { params });
    return response.data;
  },

  /**
   * Get a specific product with price history.
   */
  getProduct: async (productId: number): Promise<ProductWithHistory> => {
    const response = await apiClient.get<ProductWithHistory>(`/products/${productId}`);
    return response.data;
  },

  /**
   * Get list of all product categories.
   */
  getCategories: async (): Promise<string[]> => {
    const response = await apiClient.get<string[]>('/products/categories/list');
    return response.data;
  },
};

/**
 * User preference API endpoints.
 */
export const preferenceApi = {
  /**
   * Get current user's preferences.
   */
  getPreferences: async (): Promise<UserPreference> => {
    const response = await apiClient.get<UserPreference>('/preferences/');
    return response.data;
  },

  /**
   * Update user preferences.
   */
  updatePreferences: async (
    data: Partial<Omit<UserPreference, 'id' | 'user_id' | 'created_at' | 'updated_at'>>
  ): Promise<UserPreference> => {
    const response = await apiClient.patch<UserPreference>('/preferences/', data);
    return response.data;
  },
};

/**
 * Check if user is authenticated.
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token');
};

export default apiClient;
