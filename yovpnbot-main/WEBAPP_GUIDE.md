# 🚀 YoVPN WebApp - Полное руководство

Современный Telegram WebApp для активации подписок v2raytun с плавными анимациями, glassmorphism дизайном и UX-первым подходом.

## 📋 Оглавление

1. [Общий обзор](#общий-обзор)
2. [Архитектура](#архитектура)
3. [Установка и запуск](#установка-и-запуск)
4. [Интеграция с ботом](#интеграция-с-ботом)
5. [Деплой](#деплой)
6. [Кастомизация](#кастомизация)

---

## 🎯 Общий обзор

### Что это?

YoVPN WebApp - это Telegram Mini App, который позволяет пользователям:

1. **Выбрать платформу** (Android, iOS, macOS, Windows, Android TV)
2. **Скачать приложение** v2raytun
3. **Активировать подписку** в 1 клик через URI

### Ключевые особенности

- ✨ **Современный UI/UX** - Glassmorphism, GSAP анимации
- 🚀 **Next.js 15** - App Router, TypeScript, SSR
- 🎨 **Tailwind CSS** - Утилитарные стили
- 🔗 **Telegram Integration** - Полная интеграция с Bot API
- 📱 **PWA** - Установка как нативное приложение
- 🌓 **Dark/Light Theme** - Автоопределение темы Telegram
- 🛠️ **Dev Mode** - Тестирование без Telegram

---

## 🏗️ Архитектура

### Frontend (Next.js 15)

```
webapp/
├── src/
│   ├── app/              # Next.js 15 App Router
│   │   ├── layout.tsx    # Корневой layout с Telegram script
│   │   └── page.tsx      # Главная страница
│   ├── components/       # React компоненты
│   │   ├── PlatformSelector.tsx    # Шаг 1: выбор платформы
│   │   ├── DownloadStep.tsx        # Шаг 2: скачивание
│   │   ├── ActivationStep.tsx      # Шаг 3: активация
│   │   ├── MainApp.tsx             # Главный компонент
│   │   ├── ThemeProvider.tsx       # Управление темой
│   │   └── DevModeToggle.tsx       # Dev режим
│   ├── hooks/
│   │   ├── useTelegram.ts          # Хук для Telegram WebApp API
│   │   └── useStore.ts             # Zustand state management
│   ├── lib/
│   │   ├── api.ts                  # API клиент
│   │   ├── constants.ts            # Константы
│   │   ├── utils.ts                # Утилиты
│   │   └── pwa.ts                  # PWA функции
│   ├── types/
│   │   └── index.ts                # TypeScript типы
│   └── styles/
│       └── globals.css             # Глобальные стили
└── public/
    ├── manifest.json               # PWA manifest
    ├── sw.js                       # Service Worker
    └── icons/                      # Иконки PWA
```

### Backend (FastAPI)

```
api/
├── app/
│   ├── routes/
│   │   └── api.py                  # API endpoints
│   ├── models/
│   │   └── schemas.py              # Pydantic схемы
│   ├── services/
│   │   └── subscription_service.py # Бизнес-логика
│   ├── utils/
│   │   └── telegram.py             # Telegram валидация
│   ├── config.py                   # Конфигурация
│   └── main.py                     # FastAPI app
├── requirements.txt
└── .env
```

### Bot Integration

```
bot/handlers/
└── webapp_handler.py               # WebApp handler для бота
```

---

## 🚀 Установка и запуск

### Шаг 1: Установка зависимостей

#### Frontend
```bash
cd webapp
npm install
```

#### Backend
```bash
cd api
pip install -r requirements.txt
```

### Шаг 2: Настройка окружения

#### Frontend (.env.local)
```env
NEXT_PUBLIC_DEV_MODE=true
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NEXT_PUBLIC_TELEGRAM_BOT_TOKEN=your_bot_token

# Download URLs
NEXT_PUBLIC_ANDROID_APK_URL=https://github.com/.../v2raytun-android.apk
NEXT_PUBLIC_IOS_APP_STORE_URL=https://apps.apple.com/app/v2raytun
NEXT_PUBLIC_MACOS_DMG_URL=https://github.com/.../v2raytun-macos.dmg
NEXT_PUBLIC_WINDOWS_EXE_URL=https://github.com/.../v2raytun-windows.exe
NEXT_PUBLIC_ANDROID_TV_APK_URL=https://github.com/.../v2raytun-tv.apk
```

#### Backend (.env)
```env
TELEGRAM_BOT_TOKEN=your_bot_token
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000

# Marzban
MARZBAN_API_URL=http://localhost:8080
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=admin
```

### Шаг 3: Запуск в режиме разработки

#### Terminal 1: Backend
```bash
cd api
python -m app.main
# или
uvicorn app.main:app --reload
```

#### Terminal 2: Frontend
```bash
cd webapp
npm run dev
```

Приложения будут доступны:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Шаг 4: Тестирование

#### Dev Mode

По умолчанию включен Dev Mode. В правом нижнем углу будет кнопка 🛠️:

1. Нажмите на кнопку
2. Введите Mock User ID (например, 123456789)
3. Введите Mock Subscription URI (например, v2ray://test)
4. Сохраните настройки

Теперь можно тестировать все 3 шага без Telegram.

---

## 🔗 Интеграция с ботом

### Шаг 1: Регистрация WebApp handler

В `bot/main.py`:

```python
from bot.handlers import webapp_handler

# Регистрация роутера
dp.include_router(webapp_handler.router)
```

### Шаг 2: Обновление URL

В `bot/handlers/webapp_handler.py`:

```python
WEBAPP_URL = "https://your-webapp-domain.com"
# Для локальной разработки через ngrok:
# WEBAPP_URL = "https://abc123.ngrok.io"
```

### Шаг 3: Добавление команды в меню

```python
from aiogram.types import BotCommand

commands = [
    BotCommand(command="start", description="🏠 Главное меню"),
    BotCommand(command="webapp", description="🚀 Активировать подписку"),
    BotCommand(command="subscription", description="📊 Моя подписка"),
]

await bot.set_my_commands(commands)
```

### Шаг 4: Использование в боте

Пользователи смогут:

1. Написать `/webapp` в боте
2. Нажать кнопку "🚀 Открыть WebApp"
3. WebApp откроется прямо в Telegram

---

## 🌐 Деплой

### Вариант 1: Vercel (Frontend) + Railway (Backend)

#### Frontend на Vercel

```bash
cd webapp
npm install -g vercel
vercel login
vercel --prod
```

В Vercel Dashboard настройте environment variables:
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_TELEGRAM_BOT_TOKEN`
- и другие...

#### Backend на Railway

1. Создайте аккаунт на [Railway.app](https://railway.app)
2. Создайте новый проект
3. Подключите GitHub репозиторий
4. Укажите root directory: `api`
5. Настройте environment variables
6. Deploy!

### Вариант 2: Docker Compose

#### Создайте docker-compose.yml:

```yaml
version: '3.8'

services:
  webapp:
    build: ./webapp
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped

  api:
    build: ./api
    ports:
      - "8000:8000"
    env_file:
      - ./api/.env
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - webapp
      - api
    restart: unless-stopped
```

#### Dockerfile для webapp:

```dockerfile
FROM node:18-alpine AS base

# Dependencies
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Builder
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Runner
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

#### Dockerfile для api:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Вариант 3: VPS (Ubuntu)

```bash
# 1. Установка зависимостей
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip nginx

# 2. Клонирование репозитория
git clone https://github.com/yourusername/yovpn.git
cd yovpn

# 3. Frontend
cd webapp
npm install
npm run build
npm install -g pm2
pm2 start npm --name "webapp" -- start

# 4. Backend
cd ../api
pip3 install -r requirements.txt
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "api"

# 5. Nginx конфигурация
sudo nano /etc/nginx/sites-available/yovpn
```

Nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Активация конфига
sudo ln -s /etc/nginx/sites-available/yovpn /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL сертификат
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🎨 Кастомизация

### Изменение цветов

В `webapp/tailwind.config.ts`:

```typescript
colors: {
  primary: {
    500: '#YOUR_COLOR',  // Основной цвет
    600: '#YOUR_COLOR',  // Темнее
  },
}
```

### Добавление новой платформы

В `webapp/src/lib/constants.ts`:

```typescript
export const PLATFORMS: PlatformConfig[] = [
  // ... существующие платформы
  {
    id: 'linux',
    name: 'Linux',
    icon: '🐧',
    downloadUrl: 'https://...',
    description: 'Download for Linux',
  },
];
```

### Изменение анимаций

В `webapp/src/components/PlatformSelector.tsx`:

```typescript
// Настройте GSAP анимации
gsap.from(element, {
  y: 50,              // начальная позиция
  opacity: 0,         // прозрачность
  duration: 0.6,      // длительность
  ease: 'power3.out', // easing функция
});
```

### White-label версия

1. Измените название в `webapp/src/app/layout.tsx`
2. Замените логотипы в `webapp/public/icons/`
3. Обновите `manifest.json`
4. Измените цвета в `tailwind.config.ts`

---

## 📱 Тестирование в Telegram

### Локальная разработка с ngrok

```bash
# Установите ngrok
npm install -g ngrok

# Запустите туннель
ngrok http 3000

# Скопируйте URL (например, https://abc123.ngrok.io)
# Обновите WEBAPP_URL в bot/handlers/webapp_handler.py
```

### Настройка в BotFather

1. Откройте [@BotFather](https://t.me/BotFather)
2. `/mybots` → выберите вашего бота
3. `Bot Settings` → `Menu Button`
4. Укажите URL вашего WebApp

---

## 🐛 Troubleshooting

### WebApp не открывается

- Проверьте HTTPS (Telegram требует HTTPS)
- Убедитесь, что `telegram-web-app.js` загружен
- Проверьте консоль браузера

### API не отвечает

- Проверьте CORS настройки
- Убедитесь, что backend запущен
- Проверьте `.env` конфигурацию

### Анимации лагают

- Используйте `will-change` CSS свойство
- Оптимизируйте GSAP анимации
- Проверьте производительность в DevTools

---

## 📄 Лицензия

MIT

---

## 🤝 Поддержка

- GitHub Issues: [создать issue](https://github.com/yourusername/yovpn/issues)
- Telegram: @your_support_bot
- Email: support@yovpn.com

---

**Создано с ❤️ для YoVPN**
