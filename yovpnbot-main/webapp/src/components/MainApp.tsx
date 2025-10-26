'use client';

import { useEffect } from 'react';
import { useStore } from '@/hooks/useStore';
import { useTelegram } from '@/hooks/useTelegram';
import PlatformSelector from './PlatformSelector';
import DownloadStep from './DownloadStep';
import ActivationStep from './ActivationStep';
import DevModeToggle from './DevModeToggle';

export default function MainApp() {
  const { currentStep } = useStore();
  const { isReady, colorScheme } = useTelegram();

  useEffect(() => {
    // Set background color based on theme
    if (colorScheme === 'dark') {
      document.body.style.background = 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)';
    } else {
      document.body.style.background = 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 50%, #cbd5e1 100%)';
    }
  }, [colorScheme]);

  if (!isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mb-4" />
          <p className="text-adaptive-secondary font-semibold">Загрузка...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background Elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary-500/15 via-transparent to-primary-700/15" />
        <div className="absolute top-20 right-10 w-72 h-72 bg-primary-400/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 left-10 w-96 h-96 bg-primary-500/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      {/* Main Content */}
      <div className="relative z-10">
        {currentStep === 'platform' && <PlatformSelector />}
        {currentStep === 'download' && <DownloadStep />}
        {currentStep === 'activation' && <ActivationStep />}
      </div>

      {/* Dev Mode Toggle */}
      <DevModeToggle />
    </div>
  );
}
