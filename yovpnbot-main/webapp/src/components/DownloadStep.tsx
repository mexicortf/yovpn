'use client';

import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { PLATFORMS, ANIMATION_DURATION } from '@/lib/constants';
import { useStore } from '@/hooks/useStore';
import { useTelegram } from '@/hooks/useTelegram';
import { cn } from '@/lib/utils';

export default function DownloadStep() {
  const containerRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const [isDownloaded, setIsDownloaded] = useState(false);
  
  const {
    selectedPlatform,
    setCurrentStep,
    isDownloading,
    setIsDownloading,
    downloadProgress,
    setDownloadProgress,
  } = useStore();
  
  const { hapticFeedback, showBackButton, hideBackButton } = useTelegram();

  const platform = PLATFORMS.find(p => p.id === selectedPlatform);

  useEffect(() => {
    // Show back button
    showBackButton(() => {
      setCurrentStep('platform');
    });

    // Animate entrance
    gsap.from(containerRef.current, {
      opacity: 0,
      scale: 0.9,
      duration: ANIMATION_DURATION,
      ease: 'power3.out',
    });

    return () => {
      hideBackButton();
    };
  }, []);

  useEffect(() => {
    if (isDownloading && downloadProgress < 100) {
      const interval = setInterval(() => {
        setDownloadProgress(Math.min(downloadProgress + 10, 100));
      }, 200);

      return () => clearInterval(interval);
    } else if (downloadProgress === 100 && !isDownloaded) {
      setIsDownloaded(true);
      hapticFeedback.notification('success');
      
      // Auto-transition to activation after 1 second
      setTimeout(() => {
        handleContinue();
      }, 1500);
    }
  }, [isDownloading, downloadProgress]);

  useEffect(() => {
    if (progressRef.current && isDownloading) {
      gsap.to(progressRef.current, {
        width: `${downloadProgress}%`,
        duration: 0.3,
        ease: 'power2.out',
      });
    }
  }, [downloadProgress]);

  const handleDownload = () => {
    if (!platform) return;
    
    hapticFeedback.impact('medium');
    setIsDownloading(true);
    setDownloadProgress(0);

    // Open download link
    window.open(platform.downloadUrl, '_blank');
  };

  const handleContinue = () => {
    hapticFeedback.impact('light');
    
    gsap.to(containerRef.current, {
      opacity: 0,
      scale: 0.9,
      duration: 0.3,
      onComplete: () => {
        setCurrentStep('activation');
      },
    });
  };

  if (!platform) return null;

  return (
    <div ref={containerRef} className="flex flex-col items-center justify-center min-h-screen p-6">
      <div className="max-w-2xl w-full">
        {/* Platform Icon */}
        <div className="text-8xl text-center mb-8 animate-scale-in">
          {platform.icon}
        </div>

        {/* Title */}
        <h1 className="text-3xl md:text-4xl font-bold text-center mb-4 text-adaptive-primary">
          Скачайте v2raytun для {platform.name}
        </h1>

        {/* Description */}
        <p className="text-center text-adaptive-secondary mb-8 font-medium">
          {platform.description}
        </p>

        {/* Download Button or Progress */}
        {!isDownloading && !isDownloaded ? (
          <button
            onClick={handleDownload}
            className={cn(
              'w-full btn-primary',
              'text-xl py-4 mb-6',
              'flex items-center justify-center gap-3'
            )}
          >
            <span>📥</span>
            <span>Скачать приложение</span>
          </button>
        ) : isDownloading && !isDownloaded ? (
          <div className="mb-6">
            {/* Progress Bar */}
            <div className="glass-dark rounded-xl p-6 mb-4 border-2 border-primary-500/40">
              <div className="flex items-center justify-between mb-3">
                <span className="text-adaptive-primary font-bold text-lg">Загрузка...</span>
                <span className="text-primary-500 dark:text-primary-400 font-bold text-xl">{downloadProgress}%</span>
              </div>
              
              <div className="w-full h-4 bg-slate-700/80 dark:bg-slate-800/90 rounded-full overflow-hidden border border-slate-600/60">
                <div
                  ref={progressRef}
                  className="h-full bg-gradient-to-r from-primary-500 to-primary-400 shimmer shadow-lg"
                  style={{ width: '0%' }}
                />
              </div>
            </div>

            {/* Loading spinner */}
            <div className="flex justify-center">
              <div className="spinner" />
            </div>
          </div>
        ) : (
          <div className="mb-6">
            {/* Success Message */}
            <div className="glass-dark rounded-xl p-6 text-center border-2 border-green-500/70 glow-success shadow-2xl">
              <div className="text-6xl mb-4">✅</div>
              <h3 className="text-2xl font-bold text-green-500 dark:text-green-400 mb-2">
                Загрузка завершена!
              </h3>
              <p className="text-adaptive-primary font-semibold text-lg">
                Переходим к активации подписки...
              </p>
            </div>
          </div>
        )}

        {/* Manual Continue Button */}
        {isDownloaded && (
          <button
            onClick={handleContinue}
            className="w-full btn-secondary text-lg py-3"
          >
            Продолжить →
          </button>
        )}

        {/* Instructions */}
        {!isDownloading && (
          <div className="glass-dark rounded-xl p-6 mt-6 border border-primary-500/30 shadow-lg">
            <h3 className="text-xl font-bold text-adaptive-primary mb-4">
              📋 Инструкция:
            </h3>
            <ol className="space-y-3 text-adaptive-primary">
              <li className="flex gap-3">
                <span className="text-primary-500 dark:text-primary-400 font-bold text-lg">1.</span>
                <span className="font-semibold">Нажмите кнопку "Скачать приложение"</span>
              </li>
              <li className="flex gap-3">
                <span className="text-primary-500 dark:text-primary-400 font-bold text-lg">2.</span>
                <span className="font-semibold">Установите приложение на ваше устройство</span>
              </li>
              <li className="flex gap-3">
                <span className="text-primary-500 dark:text-primary-400 font-bold text-lg">3.</span>
                <span className="font-semibold">Вернитесь сюда для активации подписки</span>
              </li>
            </ol>
          </div>
        )}
      </div>
    </div>
  );
}
