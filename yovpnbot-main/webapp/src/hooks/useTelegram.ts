'use client';

import { useEffect, useState } from 'react';
import { TelegramWebApp } from '@/types';

export function useTelegram() {
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);
  const [user, setUser] = useState<TelegramWebApp['initDataUnsafe']['user'] | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const app = window.Telegram?.WebApp;
    
    if (app) {
      app.ready();
      app.expand();
      setWebApp(app);
      setUser(app.initDataUnsafe.user || null);
      setIsReady(true);

      // Set theme colors
      if (app.themeParams.bg_color) {
        document.documentElement.style.setProperty('--tg-bg-color', app.themeParams.bg_color);
      }
      if (app.themeParams.text_color) {
        document.documentElement.style.setProperty('--tg-text-color', app.themeParams.text_color);
      }
    } else {
      // Development mode fallback
      console.warn('Telegram WebApp not available. Running in development mode.');
      setIsReady(true);
    }
  }, []);

  const hapticFeedback = {
    impact: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
      webApp?.HapticFeedback.impactOccurred(style);
    },
    notification: (type: 'error' | 'success' | 'warning') => {
      webApp?.HapticFeedback.notificationOccurred(type);
    },
    selection: () => {
      webApp?.HapticFeedback.selectionChanged();
    },
  };

  const showMainButton = (text: string, onClick: () => void) => {
    if (webApp?.MainButton) {
      webApp.MainButton.setText(text);
      webApp.MainButton.onClick(onClick);
      webApp.MainButton.show();
    }
  };

  const hideMainButton = () => {
    webApp?.MainButton.hide();
  };

  const showBackButton = (onClick: () => void) => {
    if (webApp?.BackButton) {
      webApp.BackButton.onClick(onClick);
      webApp.BackButton.show();
    }
  };

  const hideBackButton = () => {
    webApp?.BackButton.hide();
  };

  const close = () => {
    webApp?.close();
  };

  return {
    webApp,
    user,
    isReady,
    hapticFeedback,
    showMainButton,
    hideMainButton,
    showBackButton,
    hideBackButton,
    close,
    colorScheme: webApp?.colorScheme || 'dark',
    platform: webApp?.platform || 'unknown',
  };
}
