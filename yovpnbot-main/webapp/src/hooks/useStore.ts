'use client';

import { create } from 'zustand';
import { Platform, Step, Subscription, DevModeConfig } from '@/types';

interface AppState {
  // Current step
  currentStep: Step;
  setCurrentStep: (step: Step) => void;

  // Selected platform
  selectedPlatform: Platform | null;
  setSelectedPlatform: (platform: Platform | null) => void;

  // Subscription data
  subscription: Subscription | null;
  setSubscription: (subscription: Subscription | null) => void;

  // Download state
  isDownloading: boolean;
  setIsDownloading: (isDownloading: boolean) => void;
  downloadProgress: number;
  setDownloadProgress: (progress: number) => void;

  // Activation state
  isActivating: boolean;
  setIsActivating: (isActivating: boolean) => void;
  activationSuccess: boolean;
  setActivationSuccess: (success: boolean) => void;

  // Theme
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;

  // Dev mode
  devMode: DevModeConfig;
  setDevMode: (config: DevModeConfig) => void;

  // Reset
  reset: () => void;
}

export const useStore = create<AppState>((set) => ({
  currentStep: 'platform',
  setCurrentStep: (step) => set({ currentStep: step }),

  selectedPlatform: null,
  setSelectedPlatform: (platform) => set({ selectedPlatform: platform }),

  subscription: null,
  setSubscription: (subscription) => set({ subscription: subscription }),

  isDownloading: false,
  setIsDownloading: (isDownloading) => set({ isDownloading }),
  downloadProgress: 0,
  setDownloadProgress: (progress) => set({ downloadProgress: progress }),

  isActivating: false,
  setIsActivating: (isActivating) => set({ isActivating }),
  activationSuccess: false,
  setActivationSuccess: (success) => set({ activationSuccess: success }),

  theme: 'dark',
  setTheme: (theme) => set({ theme }),

  devMode: {
    enabled: process.env.NEXT_PUBLIC_DEV_MODE === 'true',
  },
  setDevMode: (config) => set({ devMode: config }),

  reset: () =>
    set({
      currentStep: 'platform',
      selectedPlatform: null,
      isDownloading: false,
      downloadProgress: 0,
      isActivating: false,
      activationSuccess: false,
    }),
}));
