import { PlatformConfig } from '@/types';

export const PLATFORMS: PlatformConfig[] = [
  {
    id: 'android',
    name: 'Android',
    icon: '📱',
    downloadUrl: process.env.NEXT_PUBLIC_ANDROID_APK_URL || '#',
    description: 'Download for Android devices',
  },
  {
    id: 'ios',
    name: 'iOS',
    icon: '🍎',
    downloadUrl: process.env.NEXT_PUBLIC_IOS_APP_STORE_URL || '#',
    description: 'Download from App Store',
  },
  {
    id: 'macos',
    name: 'macOS',
    icon: '💻',
    downloadUrl: process.env.NEXT_PUBLIC_MACOS_DMG_URL || '#',
    description: 'Download for Mac',
  },
  {
    id: 'windows',
    name: 'Windows',
    icon: '🪟',
    downloadUrl: process.env.NEXT_PUBLIC_WINDOWS_EXE_URL || '#',
    description: 'Download for Windows',
  },
  {
    id: 'androidtv',
    name: 'Android TV',
    icon: '📺',
    downloadUrl: process.env.NEXT_PUBLIC_ANDROID_TV_APK_URL || '#',
    description: 'Download for Android TV',
  },
];

export const STEPS = {
  PLATFORM: 'platform' as const,
  DOWNLOAD: 'download' as const,
  ACTIVATION: 'activation' as const,
};

export const ANIMATION_DURATION = 0.6;
export const STAGGER_DELAY = 0.1;

export const THEME_COLORS = {
  light: {
    primary: '#0ea5e9',
    background: '#ffffff',
    text: '#1f2937',
    glass: 'rgba(255, 255, 255, 0.7)',
  },
  dark: {
    primary: '#38bdf8',
    background: '#0f172a',
    text: '#f1f5f9',
    glass: 'rgba(0, 0, 0, 0.7)',
  },
};
