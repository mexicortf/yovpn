# Исправление ошибки WebApp - Module not found

## Дата: 2025-10-21

### Проблема
```
Module not found: Can't resolve '@/lib/constants'
```

### Причина
Next.js dev server не видел файл `constants.ts` из-за кэширования или был запущен до создания файла.

---

## Решение

### 1. Проверка файлов
Все необходимые файлы уже существуют:
- ✅ `/webapp/src/lib/constants.ts` - содержит PLATFORMS, ANIMATION_DURATION, STAGGER_DELAY
- ✅ `/webapp/src/types/index.ts` - содержит типы Platform, PlatformConfig, etc.
- ✅ `/webapp/tsconfig.json` - настроен path alias `@/*`

### 2. Очистка кэша
Кэш Next.js был очищен:
```bash
cd /workspace/webapp
rm -rf .next
```

### 3. Перезапуск dev server

#### Автоматический способ (рекомендуется):
```bash
cd /workspace/webapp
./restart-dev.sh
```

#### Ручной способ:
```bash
cd /workspace/webapp

# 1. Остановите текущий dev server (Ctrl+C)

# 2. Очистите кэш
rm -rf .next

# 3. Установите зависимости (если нужно)
npm install

# 4. Запустите dev server
npm run dev
```

---

## Структура файлов webapp

```
webapp/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ActivationStep.tsx
│   │   ├── DevModeToggle.tsx
│   │   ├── DownloadStep.tsx
│   │   ├── MainApp.tsx
│   │   ├── PlatformSelector.tsx
│   │   └── ThemeProvider.tsx
│   ├── hooks/
│   │   ├── useStore.ts
│   │   └── useTelegram.ts
│   ├── lib/
│   │   ├── api.ts           ✅ API сервис
│   │   ├── constants.ts     ✅ Константы (PLATFORMS, ANIMATION_DURATION)
│   │   ├── pwa.ts          ✅ PWA утилиты
│   │   └── utils.ts        ✅ Утилиты (cn, copyToClipboard)
│   ├── styles/
│   │   └── globals.css
│   └── types/
│       └── index.ts         ✅ TypeScript типы
├── public/
├── tsconfig.json            ✅ Path aliases настроены
├── next.config.js
├── package.json
├── restart-dev.sh           ✅ Скрипт для перезапуска
└── .env.example
```

---

## Содержимое ключевых файлов

### constants.ts
```typescript
export const PLATFORMS: PlatformConfig[] = [
  {
    id: 'android',
    name: 'Android',
    icon: '📱',
    downloadUrl: process.env.NEXT_PUBLIC_ANDROID_APK_URL || '#',
    description: 'Download for Android devices',
  },
  // ... остальные платформы
];

export const ANIMATION_DURATION = 0.6;
export const STAGGER_DELAY = 0.1;
export const THEME_COLORS = { /* ... */ };
```

### tsconfig.json (path aliases)
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## Проверка после перезапуска

### 1. Проверьте, что dev server запущен:
```bash
# Должно быть:
✓ Ready in XXms
○ Compiling / ...
✓ Compiled successfully
```

### 2. Откройте в браузере:
```
http://localhost:3000
```

### 3. Проверьте консоль браузера:
- ❌ Не должно быть ошибок "Module not found"
- ✅ Должна загрузиться страница с выбором платформы

---

## Если ошибка все еще есть

### Вариант 1: Полная переустановка зависимостей
```bash
cd /workspace/webapp
rm -rf node_modules package-lock.json .next
npm install
npm run dev
```

### Вариант 2: Проверка импортов
Убедитесь, что в компонентах используется правильный синтаксис:
```typescript
// ✅ Правильно
import { PLATFORMS, ANIMATION_DURATION } from '@/lib/constants';

// ❌ Неправильно
import { PLATFORMS, ANIMATION_DURATION } from '../lib/constants';
import { PLATFORMS, ANIMATION_DURATION } from '/lib/constants';
```

### Вариант 3: Проверка версии Node.js
```bash
node --version  # Должно быть >= 18.0.0
npm --version   # Должно быть >= 9.0.0
```

---

## Переменные окружения для webapp

Создайте файл `.env.local` в `/workspace/webapp/`:

```bash
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Telegram Bot
NEXT_PUBLIC_BOT_USERNAME=your_bot_username

# Download URLs
NEXT_PUBLIC_ANDROID_APK_URL=https://example.com/v2raytun-android.apk
NEXT_PUBLIC_IOS_APP_STORE_URL=https://apps.apple.com/app/v2raytun
NEXT_PUBLIC_MACOS_DMG_URL=https://example.com/v2raytun-macos.dmg
NEXT_PUBLIC_WINDOWS_EXE_URL=https://example.com/v2raytun-windows.exe
NEXT_PUBLIC_ANDROID_TV_APK_URL=https://example.com/v2raytun-androidtv.apk

# Development
NEXT_PUBLIC_DEV_MODE=true
```

---

## Запуск в Docker

Если хотите запустить webapp в Docker:

```bash
cd /workspace
docker-compose -f docker-compose.webapp.yml up -d

# Проверка логов
docker logs -f yovpn-webapp
```

---

## Полезные команды

```bash
# Запуск dev server
npm run dev

# Сборка для продакшена
npm run build

# Запуск production сервера
npm run start

# Проверка типов TypeScript
npm run type-check

# Линтинг кода
npm run lint

# Очистка кэша и перезапуск
./restart-dev.sh
```

---

## Контакты и поддержка

Если проблема не решена:

1. Проверьте логи dev server в консоли
2. Проверьте Network в DevTools браузера
3. Убедитесь, что все файлы на месте
4. Попробуйте полную переустановку зависимостей

**Webapp готов к работе! 🚀**
