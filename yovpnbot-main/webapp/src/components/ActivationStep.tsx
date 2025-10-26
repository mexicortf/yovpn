'use client';

import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { PLATFORMS, ANIMATION_DURATION } from '@/lib/constants';
import { useStore } from '@/hooks/useStore';
import { useTelegram } from '@/hooks/useTelegram';
import { apiService } from '@/lib/api';
import { copyToClipboard, openDeepLink } from '@/lib/utils';
import { cn } from '@/lib/utils';

export default function ActivationStep() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [subscriptionUri, setSubscriptionUri] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string>('');
  
  const {
    selectedPlatform,
    setCurrentStep,
    isActivating,
    setIsActivating,
    activationSuccess,
    setActivationSuccess,
    subscription,
    setSubscription,
    devMode,
  } = useStore();
  
  const { hapticFeedback, showBackButton, hideBackButton, user } = useTelegram();

  const platform = PLATFORMS.find(p => p.id === selectedPlatform);

  useEffect(() => {
    // Show back button
    showBackButton(() => {
      setCurrentStep('download');
    });

    // Animate entrance
    gsap.from(containerRef.current, {
      opacity: 0,
      y: 30,
      duration: ANIMATION_DURATION,
      ease: 'power3.out',
    });

    // Fetch subscription
    fetchSubscription();

    return () => {
      hideBackButton();
    };
  }, []);

  const fetchSubscription = async () => {
    try {
      // Dev mode
      if (devMode.enabled && devMode.mockSubscriptionUri) {
        setSubscriptionUri(devMode.mockSubscriptionUri);
        return;
      }

      // Production mode
      const userId = user?.id || devMode.mockUserId;
      
      if (!userId) {
        setError('Не удалось получить ID пользователя');
        return;
      }

      const response = await apiService.getSubscription(userId);
      
      if (response.success && response.data) {
        setSubscriptionUri(response.data.subscriptionUri);
        setSubscription({
          userId: response.data.userId,
          subscriptionUri: response.data.subscriptionUri,
          expiresAt: response.data.expiresAt,
          isActive: true,
          subscriptionType: 'premium',
        });
      } else {
        setError(response.error || 'Не удалось получить подписку');
      }
    } catch (err) {
      console.error('Error fetching subscription:', err);
      setError('Произошла ошибка при загрузке подписки');
    }
  };

  const handleActivate = async () => {
    if (!platform) return;
    
    hapticFeedback.impact('heavy');
    setIsActivating(true);
    setError('');

    try {
      const userId = user?.id || devMode.mockUserId;
      const telegramUsername = user?.username;
      
      if (!userId) {
        setError('Не удалось получить ID пользователя');
        setIsActivating(false);
        hapticFeedback.notification('error');
        return;
      }

      console.log('🚀 Activating subscription for user:', userId, 'platform:', platform.id);

      // Call activation endpoint - this creates/updates user in Marzban
      const activationResult = await apiService.activateSubscription(
        userId,
        platform.id,
        telegramUsername
      );

      if (!activationResult.success || !activationResult.data) {
        console.error('Activation failed:', activationResult.error);
        setError(activationResult.error || 'Не удалось активировать подписку');
        setIsActivating(false);
        hapticFeedback.notification('error');
        return;
      }

      console.log('✅ Activation successful:', activationResult.data);

      // Get the subscription URI from activation result
      const activatedSubscriptionUri = activationResult.data.subscription_uri;
      
      if (!activatedSubscriptionUri) {
        setError('Не удалось получить URI подписки');
        setIsActivating(false);
        hapticFeedback.notification('error');
        return;
      }

      // Update subscription state
      setSubscriptionUri(activatedSubscriptionUri);
      setSubscription({
        userId: userId,
        subscriptionUri: activatedSubscriptionUri,
        expiresAt: activationResult.data.expires_at || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        isActive: true,
        subscriptionType: 'premium',
      });

      // Copy to clipboard
      await copyToClipboard(activatedSubscriptionUri);
      setCopied(true);
      
      // Open deep link
      setTimeout(() => {
        openDeepLink(activatedSubscriptionUri, platform.id);
      }, 500);

      // Track activation (analytics)
      await apiService.trackActivation(userId, platform.id);

      // Show success after 2 seconds
      setTimeout(() => {
        setIsActivating(false);
        setActivationSuccess(true);
        hapticFeedback.notification('success');
      }, 2000);

    } catch (err) {
      console.error('Activation error:', err);
      setIsActivating(false);
      setError('Произошла ошибка при активации подписки');
      hapticFeedback.notification('error');
    }
  };

  const handleCopyManually = async () => {
    if (!subscriptionUri) return;
    
    try {
      await copyToClipboard(subscriptionUri);
      setCopied(true);
      hapticFeedback.notification('success');
      
      setTimeout(() => setCopied(false), 3000);
    } catch (err) {
      hapticFeedback.notification('error');
    }
  };

  const handleReset = () => {
    hapticFeedback.impact('light');
    
    gsap.to(containerRef.current, {
      opacity: 0,
      scale: 0.9,
      duration: 0.3,
      onComplete: () => {
        setCurrentStep('platform');
        setActivationSuccess(false);
        setIsActivating(false);
      },
    });
  };

  if (!platform) return null;

  return (
    <div ref={containerRef} className="flex flex-col items-center justify-center min-h-screen p-6">
      <div className="max-w-2xl w-full">
        {!activationSuccess ? (
          <>
            {/* Icon */}
            <div className="text-8xl text-center mb-8 animate-scale-in">
              🔗
            </div>

            {/* Title */}
            <h1 className="text-3xl md:text-4xl font-bold text-center mb-4 text-adaptive-primary">
              Активация подписки
            </h1>

            {/* Description */}
            <p className="text-center text-adaptive-secondary mb-8 font-medium">
              Нажмите кнопку ниже, чтобы активировать подписку в v2raytun
            </p>

            {/* Error Message */}
            {error && (
              <div className="glass-dark rounded-xl p-4 mb-6 border-2 border-red-500/70 text-center shadow-xl">
                <p className="text-red-500 dark:text-red-400 font-bold text-lg">{error}</p>
              </div>
            )}

            {/* Subscription Info */}
            {subscription && !error && (
              <div className="glass-dark rounded-xl p-6 mb-6 border border-primary-500/30 shadow-xl">
                <h3 className="text-xl font-bold text-adaptive-primary mb-4">
                  ℹ️ Информация о подписке
                </h3>
                <div className="space-y-3 text-base">
                  <div className="flex justify-between">
                    <span className="text-adaptive-secondary font-semibold">Платформа:</span>
                    <span className="text-adaptive-primary font-bold">{platform.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-adaptive-secondary font-semibold">Статус:</span>
                    <span className="text-green-500 dark:text-green-400 font-bold">✓ Активна</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-adaptive-secondary font-semibold">Действует до:</span>
                    <span className="text-adaptive-primary font-bold">{new Date(subscription.expiresAt).toLocaleDateString('ru-RU')}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Activate Button */}
            {!isActivating && subscriptionUri && (
              <button
                onClick={handleActivate}
                className={cn(
                  'w-full btn-primary',
                  'text-xl py-4 mb-4',
                  'flex items-center justify-center gap-3',
                  'glow-primary'
                )}
              >
                <span>🚀</span>
                <span>Активировать подписку</span>
              </button>
            )}

            {/* Activating State */}
            {isActivating && (
              <div className="glass-dark rounded-xl p-8 mb-4 text-center border-2 border-primary-500/40 shadow-xl">
                <div className="spinner mb-4 mx-auto" />
                <p className="text-adaptive-primary font-bold text-xl">Активация...</p>
                <p className="text-adaptive-secondary text-base mt-2 font-semibold">
                  {copied ? '✅ URI скопирован в буфер обмена' : 'Открываем приложение...'}
                </p>
              </div>
            )}

            {/* Manual Copy */}
            {subscriptionUri && !isActivating && (
              <button
                onClick={handleCopyManually}
                className="w-full btn-secondary py-3 mb-6"
              >
                {copied ? '✓ Скопировано!' : '📋 Скопировать URI вручную'}
              </button>
            )}

            {/* Manual Instructions */}
            {!isActivating && (
              <div className="glass-dark rounded-xl p-6 border border-primary-500/30 shadow-lg">
                <h3 className="text-lg font-bold text-adaptive-primary mb-4">
                  📖 Если автоматическая активация не сработала:
                </h3>
                <ol className="space-y-3 text-adaptive-primary text-sm">
                  <li className="flex gap-3">
                    <span className="text-primary-500 dark:text-primary-400 font-bold">1.</span>
                    <span className="font-semibold">Скопируйте URI вручную (кнопка выше)</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary-500 dark:text-primary-400 font-bold">2.</span>
                    <span className="font-semibold">Откройте приложение v2raytun</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary-500 dark:text-primary-400 font-bold">3.</span>
                    <span className="font-semibold">Найдите опцию "Импорт конфигурации"</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary-500 dark:text-primary-400 font-bold">4.</span>
                    <span className="font-semibold">Вставьте скопированный URI</span>
                  </li>
                </ol>
              </div>
            )}
          </>
        ) : (
          /* Success State */
          <div className="text-center">
            <div className="text-9xl mb-8 animate-scale-in">
              ✅
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold mb-6 text-adaptive-primary">
              Подписка активирована!
            </h1>
            
            <p className="text-xl text-adaptive-secondary mb-8 font-medium">
              Ваша подписка успешно подключена к v2raytun
            </p>

            <div className="glass-dark rounded-xl p-8 mb-8 border-2 border-green-500/70 glow-success shadow-2xl">
              <h3 className="text-2xl font-bold text-green-500 dark:text-green-400 mb-4">
                🎉 Всё готово!
              </h3>
              <p className="text-adaptive-primary font-semibold text-lg">
                Теперь вы можете пользоваться защищённым VPN-соединением
              </p>
            </div>

            <button
              onClick={handleReset}
              className="btn-secondary text-lg py-3 px-8"
            >
              Настроить другое устройство
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
