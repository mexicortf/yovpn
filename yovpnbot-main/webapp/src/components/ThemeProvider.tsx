'use client';

import { useEffect } from 'react';
import { useStore } from '@/hooks/useStore';
import { useTelegram } from '@/hooks/useTelegram';

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme, setTheme } = useStore();
  const { colorScheme } = useTelegram();

  useEffect(() => {
    // Set theme based on Telegram color scheme
    const detectedTheme = colorScheme === 'dark' ? 'dark' : 'light';
    setTheme(detectedTheme);

    // Apply theme to document
    if (detectedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [colorScheme]);

  return <>{children}</>;
}
