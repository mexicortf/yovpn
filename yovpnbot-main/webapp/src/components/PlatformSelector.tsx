'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { PLATFORMS, ANIMATION_DURATION, STAGGER_DELAY } from '@/lib/constants';
import { useStore } from '@/hooks/useStore';
import { useTelegram } from '@/hooks/useTelegram';
import { Platform } from '@/types';
import { cn } from '@/lib/utils';

export default function PlatformSelector() {
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  
  const { setSelectedPlatform, setCurrentStep } = useStore();
  const { hapticFeedback } = useTelegram();

  useEffect(() => {
    // Animate title and subtitle
    const tl = gsap.timeline();
    
    tl.from(titleRef.current, {
      y: -30,
      opacity: 0,
      duration: ANIMATION_DURATION,
      ease: 'power3.out',
    })
    .from(subtitleRef.current, {
      y: -20,
      opacity: 0,
      duration: ANIMATION_DURATION,
      ease: 'power3.out',
    }, '-=0.3')
    .from(cardsRef.current, {
      y: 50,
      opacity: 0,
      scale: 0.9,
      duration: ANIMATION_DURATION,
      stagger: STAGGER_DELAY,
      ease: 'back.out(1.2)',
    }, '-=0.2');
  }, []);

  const handlePlatformSelect = (platform: Platform) => {
    hapticFeedback.impact('medium');
    
    // Find the selected card
    const selectedIndex = PLATFORMS.findIndex(p => p.id === platform);
    const selectedCard = cardsRef.current[selectedIndex];
    
    // Animate selection
    if (selectedCard) {
      gsap.to(selectedCard, {
        scale: 1.1,
        duration: 0.2,
        yoyo: true,
        repeat: 1,
        onComplete: () => {
          // Animate out all cards
          gsap.to(cardsRef.current, {
            opacity: 0,
            scale: 0.8,
            duration: 0.3,
            stagger: 0.05,
            onComplete: () => {
              setSelectedPlatform(platform);
              setCurrentStep('download');
            },
          });
          
          // Animate out title and subtitle
          gsap.to([titleRef.current, subtitleRef.current], {
            opacity: 0,
            y: -20,
            duration: 0.3,
          });
        },
      });
    }
  };

  const handleCardHover = (index: number, isHovering: boolean) => {
    const card = cardsRef.current[index];
    if (!card) return;

    if (isHovering) {
      hapticFeedback.selection();
      gsap.to(card, {
        y: -12,
        scale: 1.05,
        duration: 0.3,
        ease: 'power2.out',
      });
    } else {
      gsap.to(card, {
        y: 0,
        scale: 1,
        duration: 0.3,
        ease: 'power2.out',
      });
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      <div className="max-w-4xl w-full">
        {/* Title */}
        <h1
          ref={titleRef}
          className="text-4xl md:text-5xl font-bold text-center mb-4 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent"
        >
          Выберите платформу
        </h1>
        
        {/* Subtitle */}
        <p
          ref={subtitleRef}
          className="text-center text-adaptive-secondary mb-12 text-lg font-medium"
        >
          Выберите устройство для установки v2raytun
        </p>

        {/* Platform Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 md:gap-6">
          {PLATFORMS.map((platform, index) => (
            <div
              key={platform.id}
              ref={(el) => {
                cardsRef.current[index] = el;
              }}
              className={cn(
                'platform-card glass-dark rounded-2xl p-6 cursor-pointer',
                'flex flex-col items-center justify-center',
                'hover:border-primary-400 transition-all duration-300',
                'relative overflow-hidden',
                'shadow-xl hover:shadow-2xl'
              )}
              onClick={() => handlePlatformSelect(platform.id)}
              onMouseEnter={() => handleCardHover(index, true)}
              onMouseLeave={() => handleCardHover(index, false)}
            >
              {/* Background glow */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary-400/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300" />
              
              {/* Icon */}
              <div className="text-6xl mb-4 transform transition-transform duration-300 hover:scale-110">
                {platform.icon}
              </div>
              
              {/* Name */}
              <h3 className="text-lg font-bold text-adaptive-primary mb-2">
                {platform.name}
              </h3>
              
              {/* Description */}
              <p className="text-xs text-adaptive-tertiary text-center font-medium">
                {platform.description}
              </p>
            </div>
          ))}
        </div>

        {/* Decorative elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-400/30 rounded-full blur-3xl opacity-30 animate-pulse" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-primary-500/30 rounded-full blur-3xl opacity-30 animate-pulse" style={{ animationDelay: '1s' }} />
      </div>
    </div>
  );
}
