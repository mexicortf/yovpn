# 🎬 YoVPN WebApp - Animations Guide

Подробное руководство по всем анимациям в проекте.

---

## 📋 Содержание

- [GSAP Анимации](#gsap-анимации)
- [CSS Анимации](#css-анимации)
- [Haptic Feedback](#haptic-feedback)
- [Создание GIF демо](#создание-gif-демо)
- [Оптимизация производительности](#оптимизация-производительности)

---

## 🎨 GSAP Анимации

### PlatformSelector Component

#### Entrance Animation

```typescript
// webapp/src/components/PlatformSelector.tsx

useEffect(() => {
  const tl = gsap.timeline();
  
  // Анимация заголовка
  tl.from(titleRef.current, {
    y: -30,              // Начинаем выше на 30px
    opacity: 0,          // Полностью прозрачный
    duration: 0.6,       // 600ms
    ease: 'power3.out',  // Плавное замедление
  })
  
  // Анимация подзаголовка
  .from(subtitleRef.current, {
    y: -20,
    opacity: 0,
    duration: 0.6,
    ease: 'power3.out',
  }, '-=0.3')  // Начать на 300ms раньше (overlap)
  
  // Анимация карточек с stagger
  .from(cardsRef.current, {
    y: 50,               // Снизу вверх
    opacity: 0,
    scale: 0.9,          // Немного меньше
    duration: 0.6,
    stagger: 0.1,        // Задержка между карточками
    ease: 'back.out(1.2)', // Пружинящий эффект
  }, '-=0.2');
}, []);
```

**Результат:**
1. Заголовок плавно спускается сверху
2. Подзаголовок появляется чуть позже
3. Карточки "выпрыгивают" снизу одна за другой

#### Hover Effect

```typescript
const handleCardHover = (index: number, isHovering: boolean) => {
  const card = cardsRef.current[index];
  
  if (isHovering) {
    // При наведении
    gsap.to(card, {
      y: -12,          // Поднимаем вверх
      scale: 1.05,     // Увеличиваем на 5%
      duration: 0.3,
      ease: 'power2.out',
    });
  } else {
    // При уходе курсора
    gsap.to(card, {
      y: 0,
      scale: 1,
      duration: 0.3,
      ease: 'power2.out',
    });
  }
};
```

**Результат:**
- Карточка плавно поднимается и увеличивается при наведении
- Возвращается на место при уходе курсора

#### Selection Animation

```typescript
const handlePlatformSelect = (platform: Platform) => {
  const selectedCard = cardsRef.current[selectedIndex];
  
  // "Пульсация" выбранной карточки
  gsap.to(selectedCard, {
    scale: 1.1,
    duration: 0.2,
    yoyo: true,        // Туда и обратно
    repeat: 1,         // 1 повтор (итого 2 раза)
    onComplete: () => {
      // После пульсации - исчезновение всех карточек
      gsap.to(cardsRef.current, {
        opacity: 0,
        scale: 0.8,
        duration: 0.3,
        stagger: 0.05,
        onComplete: () => {
          setCurrentStep('download');
        },
      });
    },
  });
};
```

**Результат:**
1. Выбранная карточка "пульсирует" (увеличивается и уменьшается)
2. Все карточки плавно исчезают
3. Переход к следующему шагу

---

### DownloadStep Component

#### Progress Bar Animation

```typescript
useEffect(() => {
  if (progressRef.current && isDownloading) {
    gsap.to(progressRef.current, {
      width: `${downloadProgress}%`,
      duration: 0.3,
      ease: 'power2.out',
    });
  }
}, [downloadProgress]);
```

С CSS shimmer эффектом:

```css
.shimmer {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 2s linear infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

**Результат:**
- Progress bar плавно заполняется
- Сияющий эффект движется слева направо

---

### ActivationStep Component

#### Success Animation

```typescript
// После успешной активации
setTimeout(() => {
  setActivationSuccess(true);
  hapticFeedback.notification('success');
  
  // Можно добавить confetti эффект
  // import confetti from 'canvas-confetti';
  // confetti({ particleCount: 100, spread: 70 });
}, 2000);
```

---

## 🎯 CSS Анимации

### Keyframe Animations

Определены в `webapp/src/styles/globals.css`:

#### 1. Fade In

```css
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-in {
  animation: fadeIn 0.6s ease-out;
}
```

#### 2. Slide Up

```css
@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.slide-up {
  animation: slideUp 0.6s ease-out;
}
```

#### 3. Scale In

```css
@keyframes scaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.scale-in {
  animation: scaleIn 0.4s ease-out;
}
```

#### 4. Glow Effect

```css
@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(14, 165, 233, 0.5);
  }
  50% {
    box-shadow: 0 0 40px rgba(14, 165, 233, 0.8);
  }
}

.glow-primary {
  animation: glow 2s ease-in-out infinite;
}
```

#### 5. Spinner

```css
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  width: 40px;
  height: 40px;
  animation: spin 1s ease-in-out infinite;
}
```

### Glassmorphism Effects

```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.glass-dark {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Platform Card Effects

```css
.platform-card {
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
}

.platform-card:hover {
  transform: translateY(-8px) scale(1.02);
}

.platform-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: inherit;
  opacity: 0;
  transition: opacity 0.3s ease;
  background: radial-gradient(
    circle at center,
    rgba(14, 165, 233, 0.15) 0%,
    transparent 70%
  );
}

.platform-card:hover::before {
  opacity: 1;
}
```

---

## 📱 Haptic Feedback

Интеграция с Telegram WebApp API для тактильной отдачи:

### Типы вибраций

```typescript
// webapp/src/hooks/useTelegram.ts

const hapticFeedback = {
  // Легкий удар (для мелких взаимодействий)
  impact: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => {
    webApp?.HapticFeedback.impactOccurred(style);
  },
  
  // Уведомление (для результатов действий)
  notification: (type: 'error' | 'success' | 'warning') => {
    webApp?.HapticFeedback.notificationOccurred(type);
  },
  
  // Выбор (для переключения опций)
  selection: () => {
    webApp?.HapticFeedback.selectionChanged();
  },
};
```

### Примеры использования

```typescript
// При выборе платформы
const handlePlatformSelect = (platform: Platform) => {
  hapticFeedback.impact('medium');
  // ...
};

// При наведении на карточку
const handleCardHover = (index: number, isHovering: boolean) => {
  if (isHovering) {
    hapticFeedback.selection();
  }
  // ...
};

// При успешной активации
setActivationSuccess(true);
hapticFeedback.notification('success');

// При ошибке
setError('Failed to activate');
hapticFeedback.notification('error');
```

---

## 🎥 Создание GIF демо

### Инструменты

#### macOS
```bash
# 1. Записать экран (QuickTime Player)
# File → New Screen Recording

# 2. Конвертировать в GIF
brew install ffmpeg
ffmpeg -i screen-recording.mov \
  -vf "fps=30,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 \
  output.gif
```

#### Windows
```bash
# Используйте ScreenToGif
# https://www.screentogif.com/

# Или FFmpeg
ffmpeg -i screen-recording.mp4 ^
  -vf "fps=30,scale=800:-1:flags=lanczos" ^
  output.gif
```

#### Linux
```bash
# Byzanz
sudo apt-get install byzanz
byzanz-record --duration=10 --x=0 --y=0 --width=800 --height=600 output.gif

# Или FFmpeg (как macOS)
```

### Рекомендуемые сцены для GIF

#### 1. platform-selection.gif
**Что показать:**
- Загрузка страницы с fade-in анимацией
- Наведение на несколько карточек
- Выбор платформы (например, Android)
- Переход к следующему шагу

**Настройки:**
- Размер: 800x600px
- FPS: 30
- Длительность: 5-7 секунд
- Loop: yes

#### 2. download-progress.gif
**Что показать:**
- Нажатие кнопки "Скачать"
- Progress bar с shimmer эффектом
- Завершение загрузки
- Success checkmark

**Настройки:**
- Размер: 600x400px
- FPS: 30
- Длительность: 3-4 секунды

#### 3. activation-success.gif
**Что показать:**
- Кнопка "Активировать подписку" с glow
- Процесс активации (spinner)
- Success animation
- Confetti эффект (опционально)

**Настройки:**
- Размер: 600x400px
- FPS: 30
- Длительность: 4-5 секунд

#### 4. theme-switch.gif
**Что показать:**
- Dark theme
- Smooth transition
- Light theme
- Обратно в dark

**Настройки:**
- Размер: 800x600px
- FPS: 30
- Длительность: 3-4 секунды

#### 5. full-flow.gif
**Что показать:**
- Весь процесс от начала до конца
- Все 3 шага

**Настройки:**
- Размер: 800x600px
- FPS: 30
- Длительность: 15-20 секунд

### Оптимизация GIF

```bash
# Уменьшить размер файла
gifsicle -O3 --colors 256 input.gif -o output.gif

# Или используйте онлайн сервис
# https://ezgif.com/optimize
```

### Размещение в README

```markdown
## 🎬 Демонстрация

### Выбор платформы
![Platform Selection](./webapp/public/demo/platform-selection.gif)

### Скачивание
![Download Progress](./webapp/public/demo/download-progress.gif)

### Активация
![Activation Success](./webapp/public/demo/activation-success.gif)
```

---

## ⚡ Оптимизация производительности

### 1. will-change CSS property

```css
.platform-card {
  will-change: transform, opacity;
}

/* Но убирайте после анимации! */
.platform-card:not(:hover) {
  will-change: auto;
}
```

### 2. GSAP Performance Tips

```typescript
// ❌ Плохо - анимация каждого свойства отдельно
gsap.to(element, { x: 100 });
gsap.to(element, { y: 50 });
gsap.to(element, { opacity: 0 });

// ✅ Хорошо - все свойства вместе
gsap.to(element, { 
  x: 100, 
  y: 50, 
  opacity: 0 
});
```

### 3. Debounce для hover

```typescript
import { debounce } from 'lodash';

const handleCardHover = debounce((index: number, isHovering: boolean) => {
  // ... animation code
}, 50);
```

### 4. Lazy loading компонентов

```typescript
import dynamic from 'next/dynamic';

const ActivationStep = dynamic(() => import('./ActivationStep'), {
  loading: () => <div>Loading...</div>,
});
```

### 5. Reduce motion для accessibility

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

```typescript
// Проверка в JS
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

if (!prefersReducedMotion) {
  // Запускать анимации
  gsap.to(element, { ... });
}
```

---

## 📊 Метрики анимаций

### Целевые показатели

| Метрика | Целевое значение |
|---------|------------------|
| First Paint | < 100ms |
| Animation FPS | 60 FPS |
| Jank (dropped frames) | < 1% |
| CPU Usage | < 30% |
| Memory | < 50MB |

### Измерение производительности

```typescript
// Chrome DevTools Performance API
const performanceObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Animation:', entry.name, entry.duration);
  }
});

performanceObserver.observe({ entryTypes: ['measure'] });

// Измерение анимации
performance.mark('animation-start');
gsap.to(element, { 
  x: 100, 
  onComplete: () => {
    performance.mark('animation-end');
    performance.measure('animation', 'animation-start', 'animation-end');
  }
});
```

---

## 🎓 Best Practices

### 1. Используйте transform и opacity

```css
/* ✅ Хорошо - GPU accelerated */
transform: translateX(100px);
opacity: 0.5;

/* ❌ Плохо - вызывает reflow */
left: 100px;
width: 200px;
```

### 2. Батчите анимации

```typescript
// ❌ Плохо
cards.forEach(card => {
  gsap.to(card, { opacity: 0 });
});

// ✅ Хорошо
gsap.to(cards, { opacity: 0, stagger: 0.1 });
```

### 3. Cleanup анимаций

```typescript
useEffect(() => {
  const tl = gsap.timeline();
  
  tl.from(element, { ... });
  
  // Cleanup при unmount
  return () => {
    tl.kill();
  };
}, []);
```

---

## 📚 Ресурсы

- [GSAP Documentation](https://greensock.com/docs/)
- [CSS Animations MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations)
- [Web Animation API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)
- [Performance Tips](https://web.dev/animations/)

---

**Happy Animating! ✨**
