import axios from 'axios';
import { ApiResponse, SubscriptionResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Add Telegram WebApp init data for authentication
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      config.headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Get subscription for current user
  async getSubscription(userId: number): Promise<ApiResponse<SubscriptionResponse>> {
    try {
      const response = await api.get(`/api/subscription/${userId}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch subscription',
      };
    }
  },

  // Validate Telegram init data
  async validateTelegramData(initData: string): Promise<ApiResponse<{ valid: boolean }>> {
    try {
      const response = await api.post('/api/validate', { initData });
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Validation failed',
      };
    }
  },

  // Get latest app version
  async getLatestVersion(platform: string): Promise<ApiResponse<{ version: string; downloadUrl: string }>> {
    try {
      const response = await api.get(`/api/version/${platform}`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch version',
      };
    }
  },

  // Track activation
  async trackActivation(userId: number, platform: string): Promise<ApiResponse<{ success: boolean }>> {
    try {
      const response = await api.post('/api/track/activation', { userId, platform });
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to track activation',
      };
    }
  },

  // Activate subscription - creates/updates user in Marzban
  async activateSubscription(
    userId: number, 
    platform: string, 
    telegramUsername?: string
  ): Promise<ApiResponse<{
    success: boolean;
    message: string;
    subscription_uri?: string;
    expires_at?: string;
    marzban_username?: string;
  }>> {
    try {
      const response = await api.post('/api/subscription/activate', {
        user_id: userId,
        platform,
        telegram_username: telegramUsername,
      });
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || error.response?.data?.message || 'Failed to activate subscription',
      };
    }
  },
};

export default api;
