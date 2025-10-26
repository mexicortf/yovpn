# YoVPN WebApp 🚀

Современный WebApp для Telegram Mini Apps, предназначенный для активации подписок v2raytun.

## ✨ Особенности

- 🎨 **Современный дизайн** - Glassmorphism, плавные GSAP-анимации
- 📱 **3 простых шага** - Выбор платформы → Скачивание → Активация
- 🌓 **Темная/Светлая тема** - Автоматическое определение темы Telegram
- 🔗 **1-Click активация** - Автоматическое копирование и открытие приложения
- 📲 **PWA поддержка** - Установка как нативное приложение
- 🛠️ **Режим разработчика** - Тестирование без Telegram
- 🚀 **Next.js 15** - App Router, TypeScript, React Server Components

## 🏗️ Архитектура

```
webapp/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/       # React компоненты
│   │   ├── PlatformSelector.tsx    # Шаг 1
│   │   ├── DownloadStep.tsx        # Шаг 2
│   │   ├── ActivationStep.tsx      # Шаг 3
│   │   ├── MainApp.tsx
│   │   ├── ThemeProvider.tsx
│   │   └── DevModeToggle.tsx
│   ├── hooks/           # React хуки
│   │   ├── useTelegram.ts
│   │   └── useStore.ts
│   ├── lib/             # Утилиты
│   │   ├── api.ts
│   │   ├── constants.ts
│   │   ├── utils.ts
│   │   └── pwa.ts
│   ├── types/           # TypeScript типы
│   │   └── index.ts
│   └── styles/          # Глобальные стили
│       └── globals.css
├── public/              # Статические файлы
│   ├── manifest.json
│   ├── sw.js
│   └── icons/
└── package.json
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd webapp
npm install
```

### 2. Настройка окружения

Создайте файл `.env.local`:

```env
# Development Mode
NEXT_PUBLIC_DEV_MODE=true

# API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000

# Telegram
NEXT_PUBLIC_TELEGRAM_BOT_TOKEN=your_bot_token

# Download URLs
NEXT_PUBLIC_ANDROID_APK_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-android.apk
NEXT_PUBLIC_IOS_APP_STORE_URL=https://apps.apple.com/app/v2raytun
NEXT_PUBLIC_MACOS_DMG_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-macos.dmg
NEXT_PUBLIC_WINDOWS_EXE_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-windows.exe
NEXT_PUBLIC_ANDROID_TV_APK_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-tv.apk
```

### 3. Запуск в режиме разработки

```bash
npm run dev
```

WebApp будет доступен по адресу: http://localhost:3000

### 4. Режим разработчика

По умолчанию включен Dev Mode для тестирования без Telegram. В правом нижнем углу появится кнопка 🛠️ для настройки мок-данных:

- **Mock User ID** - ID пользователя для тестирования
- **Mock Subscription URI** - Тестовый URI подписки

## 📦 Production Build

```bash
npm run build
npm start
```

## 🔗 Интеграция с Telegram Bot

### 1. Добавьте хендлер в бот

Файл уже создан: `/workspace/bot/handlers/webapp_handler.py`

### 2. Зарегистрируйте роутер

В `bot/main.py`:

```python
from bot.handlers import webapp_handler

# Регистрация хендлера
dp.include_router(webapp_handler.router)
```

### 3. Обновите URL WebApp

В `bot/handlers/webapp_handler.py` замените:

```python
WEBAPP_URL = "https://your-webapp-domain.com"
```

### 4. Добавьте команду в меню

```python
from bot.handlers.webapp_handler import add_webapp_to_main_menu

commands = await add_webapp_to_main_menu()
await bot.set_my_commands(commands)
```

## 🎨 UI/UX Особенности

### GSAP Анимации

- **Fade In** - Плавное появление элементов
- **Slide Up** - Скольжение снизу вверх
- **Scale In** - Увеличение с анимацией
- **Parallax** - 3D эффекты при наведении
- **Glow** - Светящиеся акценты

### Glassmorphism

- Полупрозрачные фоны с размытием
- Тонкие границы
- Световые эффекты
- Градиенты

### Responsive Design

- Mobile-first подход
- Адаптация под все размеры экранов
- Touch-friendly интерфейс
- Haptic Feedback для Telegram

## 🛠️ Технологии

- **Next.js 15** - React фреймворк
- **TypeScript** - Типизация
- **Tailwind CSS** - Стилизация
- **GSAP** - Анимации
- **Zustand** - State management
- **Axios** - HTTP клиент

## 📱 PWA Функции

- Установка на домашний экран
- Offline поддержка
- Service Worker кэширование
- Нативный вид приложения

## 🔐 Безопасность

- Валидация Telegram init data
- HMAC подпись проверка
- Защита от CSRF
- Безопасная передача данных

## 📊 API Endpoints

### GET /api/subscription/:userId
Получить подписку пользователя

### POST /api/validate
Валидация Telegram init data

### GET /api/version/:platform
Получить последнюю версию для платформы

### POST /api/track/activation
Отслеживание активаций

## 🎯 Roadmap

- [ ] A/B тестирование UI/UX
- [ ] Аналитика событий
- [ ] Мультиязычность
- [ ] Персонализация анимаций
- [ ] Интеграция с Apple Pay / Google Pay

## 📄 Лицензия

MIT

## 👨‍💻 Разработка

Создано для YoVPN - современного VPN-сервиса с акцентом на UX и безопасность.
