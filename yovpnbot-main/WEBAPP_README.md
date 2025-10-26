# 🚀 YoVPN WebApp - Complete Solution

> Современный Telegram Mini App для активации подписок v2raytun с glassmorphism дизайном, плавными GSAP-анимациями и UX-first подходом в стиле 2025-2026.

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js" />
  <img src="https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react" />
  <img src="https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript" />
  <img src="https://img.shields.io/badge/FastAPI-Latest-green?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/Tailwind-3-38bdf8?style=for-the-badge&logo=tailwind-css" />
  <img src="https://img.shields.io/badge/GSAP-3-88CE02?style=for-the-badge&logo=greensock" />
</p>

---

## 📋 Содержание

- [Что это?](#что-это)
- [Особенности](#особенности)
- [Быстрый старт](#быстрый-старт)
- [Архитектура](#архитектура)
- [Документация](#документация)
- [Скриншоты](#скриншоты)
- [Деплой](#деплой)

---

## 🎯 Что это?

YoVPN WebApp — это полноценное решение для активации VPN-подписок через Telegram Mini App. Пользователи могут:

1. **Выбрать платформу** — Android, iOS, macOS, Windows, Android TV
2. **Скачать приложение** — Прямые ссылки на загрузку v2raytun
3. **Активировать подписку** — В 1 клик через URI

### 🎬 User Flow

```
Telegram Bot → WebApp Button → Platform Selection → Download → Activation → Success!
     ↓              ↓                  ↓                ↓            ↓           ↓
  /webapp      WebApp opens    Beautiful UI    Auto-download   URI copy   Connected ✅
```

---

## ✨ Особенности

### 🎨 UI/UX

- **Glassmorphism** — Полупрозрачные элементы с размытием
- **GSAP Анимации** — Плавные переходы, параллакс, hover-эффекты
- **Apple-style Design** — Минимализм, чистые линии, акценты
- **Responsive** — Идеально работает на всех устройствах
- **Dark/Light Theme** — Автоматическое определение темы Telegram

### ⚡ Технологии

#### Frontend
- **Next.js 15** — App Router, SSR, TypeScript
- **React 18** — Server Components, Suspense
- **Tailwind CSS** — Утилитарные стили
- **GSAP** — Профессиональные анимации
- **Zustand** — Легковесный state management

#### Backend
- **FastAPI** — Высокопроизводительный Python фреймворк
- **Pydantic** — Валидация данных
- **HTTPX** — Async HTTP клиент
- **Telegram Bot API** — HMAC валидация

#### DevOps
- **Docker** — Контейнеризация
- **Nginx** — Reverse proxy
- **PM2** — Process manager
- **GitHub Actions** — CI/CD (опционально)

### 🔐 Безопасность

- ✅ HMAC-SHA256 валидация Telegram данных
- ✅ CORS protection
- ✅ Rate limiting (опционально)
- ✅ Secure environment variables
- ✅ HTTPS only

### 📱 PWA Support

- ✅ Offline режим
- ✅ Установка на домашний экран
- ✅ Service Worker кэширование
- ✅ Push notifications (опционально)

---

## 🚀 Быстрый старт

### Автоматический запуск (Рекомендуется)

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/yovpn.git
cd yovpn

# Запустите скрипт
./start-webapp.sh
```

Скрипт автоматически:
1. Установит все зависимости
2. Создаст .env файлы (если их нет)
3. Запустит Frontend (http://localhost:3000)
4. Запустит Backend (http://localhost:8000)

### Ручной запуск

#### 1. Frontend

```bash
cd webapp
npm install
npm run dev
```

#### 2. Backend

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

### Остановка

```bash
./stop-webapp.sh
```

---

## 🏗️ Архитектура

```
yovpn/
├── webapp/                    # Next.js Frontend
│   ├── src/
│   │   ├── app/              # App Router
│   │   ├── components/       # React компоненты
│   │   │   ├── PlatformSelector.tsx    # Шаг 1
│   │   │   ├── DownloadStep.tsx        # Шаг 2
│   │   │   ├── ActivationStep.tsx      # Шаг 3
│   │   │   ├── MainApp.tsx
│   │   │   └── ...
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # Утилиты, API
│   │   ├── types/            # TypeScript типы
│   │   └── styles/           # Стили
│   ├── public/               # Статика, PWA
│   └── package.json
│
├── api/                      # FastAPI Backend
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── models/          # Pydantic схемы
│   │   ├── services/        # Бизнес-логика
│   │   ├── utils/           # Утилиты
│   │   └── main.py
│   └── requirements.txt
│
├── bot/                      # Telegram Bot (existing)
│   ├── handlers/
│   │   └── webapp_handler.py    # NEW: WebApp handler
│   └── ...
│
├── docker-compose.webapp.yml # Docker Compose конфиг
├── nginx.conf                # Nginx конфигурация
├── start-webapp.sh          # Скрипт запуска
├── stop-webapp.sh           # Скрипт остановки
└── WEBAPP_GUIDE.md          # Полное руководство
```

---

## 📚 Документация

### Основная документация

- [📖 WEBAPP_GUIDE.md](./WEBAPP_GUIDE.md) — Полное руководство по WebApp
- [🚀 DEPLOYMENT.md](./DEPLOYMENT.md) — Руководство по деплою
- [📘 webapp/README.md](./webapp/README.md) — Frontend документация
- [📗 api/README.md](./api/README.md) — Backend API документация

### Быстрые ссылки

- **Frontend Dev**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

---

## 🎨 Скриншоты

### Шаг 1: Выбор платформы

```
┌─────────────────────────────────────────┐
│                                         │
│       Выберите платформу                │
│                                         │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐        │
│  │ 📱 │  │ 🍎 │  │ 💻 │  │ 🪟 │        │
│  │AND │  │ iOS│  │ MAC│  │ WIN│        │
│  └────┘  └────┘  └────┘  └────┘        │
│                                         │
│  ┌────┐                                 │
│  │ 📺 │                                 │
│  │ TV │                                 │
│  └────┘                                 │
│                                         │
└─────────────────────────────────────────┘
   Glassmorphism + GSAP Animations ✨
```

### Шаг 2: Скачивание

```
┌─────────────────────────────────────────┐
│                                         │
│            📱 Android                   │
│                                         │
│   Скачайте v2raytun для Android        │
│                                         │
│   ┌───────────────────────────┐        │
│   │  📥 Скачать приложение     │        │
│   └───────────────────────────┘        │
│                                         │
│   ▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ 75%             │
│                                         │
└─────────────────────────────────────────┘
```

### Шаг 3: Активация

```
┌─────────────────────────────────────────┐
│                                         │
│        🔗 Активация подписки            │
│                                         │
│   ┌───────────────────────────┐        │
│   │ 🚀 Активировать подписку   │        │
│   └───────────────────────────┘        │
│                                         │
│   📋 Скопировать URI вручную            │
│                                         │
│   ✅ Подписка активирована!             │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🌐 Деплой

### Быстрый деплой

#### Vercel (Frontend) + Railway (Backend)

1. **Frontend:**
   ```bash
   cd webapp
   vercel --prod
   ```

2. **Backend:**
   - Откройте [Railway.app](https://railway.app)
   - Deploy from GitHub
   - Root directory: `api`

#### Docker Compose

```bash
docker-compose -f docker-compose.webapp.yml up -d
```

### Полная инструкция

См. [DEPLOYMENT.md](./DEPLOYMENT.md) для детальных инструкций по деплою на:
- Vercel + Railway
- Docker Compose
- VPS (Ubuntu)
- Cloudflare Pages

---

## 🔗 Интеграция с ботом

### 1. Регистрация handler

В `bot/main.py`:

```python
from bot.handlers import webapp_handler

dp.include_router(webapp_handler.router)
```

### 2. Обновление URL

В `bot/handlers/webapp_handler.py`:

```python
WEBAPP_URL = "https://your-domain.com"
```

### 3. Команды бота

```
/webapp - Открыть WebApp для активации
```

---

## 🛠️ Режим разработчика

По умолчанию включен Dev Mode для тестирования без Telegram.

### Активация

В `webapp/.env.local`:

```env
NEXT_PUBLIC_DEV_MODE=true
```

### Использование

1. Нажмите 🛠️ в правом нижнем углу
2. Введите Mock User ID (например, 123456789)
3. Введите Mock Subscription URI
4. Сохраните и тестируйте!

---

## 📊 API Endpoints

### Health Check
```http
GET /api/health
```

### Get Subscription
```http
GET /api/subscription/:userId
```

### Validate Telegram Data
```http
POST /api/validate
```

### Track Activation
```http
POST /api/track/activation
```

Полная документация: http://localhost:8000/docs

---

## 🎯 Roadmap

- [x] Базовый функционал (3 шага)
- [x] GSAP анимации
- [x] Glassmorphism UI
- [x] PWA поддержка
- [x] Dev режим
- [x] Docker поддержка
- [ ] A/B тестирование UI/UX
- [ ] Аналитика (Google Analytics)
- [ ] Мультиязычность (i18n)
- [ ] Deep linking оптимизация
- [ ] Rate limiting
- [ ] Redis кэширование
- [ ] WebSocket для real-time статусов

---

## 🤝 Вклад

Contributions are welcome! 

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing`)
5. Откройте Pull Request

---

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

## 💬 Поддержка

- **GitHub Issues**: [Create Issue](https://github.com/yourusername/yovpn/issues)
- **Telegram**: @your_support_bot
- **Email**: support@yovpn.com
- **Документация**: [WEBAPP_GUIDE.md](./WEBAPP_GUIDE.md)

---

## 🙏 Благодарности

- [Next.js](https://nextjs.org/) - React Framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web Framework
- [GSAP](https://greensock.com/gsap/) - Animation Library
- [Tailwind CSS](https://tailwindcss.com/) - CSS Framework
- [Telegram Bot API](https://core.telegram.org/bots/api) - Bot Platform

---

<p align="center">
  <b>Создано с ❤️ для YoVPN</b><br>
  <sub>Modern VPN Service with Focus on UX & Security</sub>
</p>

<p align="center">
  <a href="#быстрый-старт">Начать</a> •
  <a href="./WEBAPP_GUIDE.md">Руководство</a> •
  <a href="./DEPLOYMENT.md">Деплой</a> •
  <a href="#поддержка">Поддержка</a>
</p>
