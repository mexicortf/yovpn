# 🏗️ Архитектура YoVPN на Railway

## 📊 Общая схема

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAILWAY PLATFORM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Redis DB   │    │ Telegram Bot │    │      API     │      │
│  │              │◄───┤              │    │   Backend    │      │
│  │ Port: 6379   │    │ Python 3.11  │    │  FastAPI     │      │
│  │              │    │              │    │              │      │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘      │
│         ▲                   │                    │              │
│         │                   │                    │              │
│         └───────────────────┴────────────────────┘              │
│                             │                    │              │
│                             │              ┌─────▼──────┐       │
│                             │              │   WebApp   │       │
│                             │              │  Next.js   │       │
│                             │              │ Port: 3000 │       │
│                             │              └─────┬──────┘       │
│                             │                    │              │
└─────────────────────────────┼────────────────────┼──────────────┘
                              │                    │
                              ▼                    ▼
                    ┌──────────────────┐  ┌──────────────────┐
                    │  Telegram Users  │  │  Browser Users   │
                    │   (Bot Chat)     │  │  (WebApp URL)    │
                    └──────────────────┘  └──────────────────┘
                              │                    │
                              └────────┬───────────┘
                                       ▼
                              ┌──────────────────┐
                              │  Marzban Server  │
                              │  (External VPN)  │
                              └──────────────────┘
```

## 🔄 Поток данных

### 1. Пользователь взаимодействует с ботом

```
User → Telegram → Bot Service → Redis (кэш) → Marzban API
                       ↓
                User Service
                       ↓
              Payment Service
```

### 2. Пользователь открывает WebApp

```
User → WebApp URL → Next.js Server → API Backend → Marzban
                         ↓
                   React Components
                         ↓
                 Telegram WebApp SDK
```

### 3. Активация подписки

```
User clicks "Activate"
      ↓
WebApp → API → Marzban → Create User → Return Config
      ↓
WebApp displays QR Code + Connection Details
      ↓
User connects to VPN
```

## 🚀 Railway Services

### 1️⃣ Redis Service
- **Type**: Database
- **Image**: `redis:7-alpine`
- **Port**: 6379 (internal)
- **Purpose**: Кэширование пользовательских данных, rate limiting
- **Storage**: In-memory + persistence
- **URL**: `${{Redis.REDIS_URL}}`

### 2️⃣ Telegram Bot Service
- **Type**: Python Application
- **Runtime**: Python 3.11
- **Framework**: Aiogram 3.4
- **Port**: Не требуется (long polling)
- **Start Command**: `python bot/main.py`
- **Dockerfile**: `/Dockerfile`
- **Dependencies**:
  - Redis (кэширование)
  - Marzban API (управление VPN)

**Функции**:
- Обработка команд пользователей
- Управление подписками
- Прием платежей
- Уведомления
- Админ-панель

### 3️⃣ API Backend Service
- **Type**: Python API
- **Runtime**: Python 3.11
- **Framework**: FastAPI
- **Port**: `$PORT` (auto-assigned)
- **Root Directory**: `api`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Public URL**: ✅ Требуется (Generate Domain)
- **Health Check**: `/health`

**Endpoints**:
- `GET /api/health` - Health check
- `GET /api/subscriptions/{user_id}` - Get user subscription
- `POST /api/activate` - Activate subscription
- `GET /docs` - API Documentation (Swagger)

### 4️⃣ WebApp Frontend Service
- **Type**: Next.js Application
- **Runtime**: Node.js 18
- **Framework**: Next.js 15
- **Port**: 3000
- **Root Directory**: `webapp`
- **Build**: `npm install && npm run build`
- **Start Command**: `npm start`
- **Public URL**: ✅ Требуется (Generate Domain)
- **Output Mode**: Standalone (Docker)

**Features**:
- React 18 + TypeScript
- Tailwind CSS styling
- GSAP animations
- Telegram WebApp SDK
- PWA support

## 🔐 Безопасность

### Переменные окружения

```
Секретные переменные (требуют защиты):
├── TELEGRAM_BOT_TOKEN (критический)
├── SECRET_KEY (критический)
├── MARZBAN_PASSWORD (критический)
└── REDIS_URL (автоматический)

Публичные переменные:
├── NEXT_PUBLIC_API_BASE_URL
├── NEXT_PUBLIC_BASE_URL
└── NEXT_PUBLIC_TELEGRAM_BOT_TOKEN
```

### Сетевая безопасность

```
Railway Network:
├── Internal Network (services communicate)
│   ├── Bot ↔ Redis (private)
│   └── API ↔ Redis (private)
│
├── External Access (via HTTPS)
│   ├── API (public domain)
│   └── WebApp (public domain)
│
└── CORS Protection
    └── API allows only WebApp domain
```

### Rate Limiting

```
Bot:
├── Per user: 10 requests/minute
└── Global: 1000 requests/minute

API:
├── Per IP: 100 requests/minute
└── Per endpoint: varies
```

## 💾 Хранение данных

### SQLite Database (Bot)
```
data/bot.db
├── users (user_id, telegram_id, username)
├── subscriptions (user_id, status, expires_at)
├── payments (user_id, amount, timestamp)
└── admin_logs (action, timestamp)
```

### Redis Cache
```
redis:
├── user:{user_id} (user data, TTL: 1h)
├── subscription:{user_id} (subscription info, TTL: 5m)
├── rate_limit:{user_id} (request counter, TTL: 1m)
└── marzban_token (API token, TTL: 1h)
```

## 📊 Масштабирование

### Railway Resources

```
Free Tier:
├── Memory: 512MB per service
├── CPU: Shared
├── Storage: 1GB
└── Credits: $5/month

Pro Tier:
├── Memory: 8GB per service
├── CPU: Dedicated
├── Storage: 100GB
└── Pay as you go
```

### Рекомендации

```
Development:
└── Free tier (все 4 сервиса)

Production (< 1000 users):
├── Bot: 512MB (Free)
├── API: 512MB (Free)
├── WebApp: 512MB (Free)
└── Redis: Upgraded (Pro)

Production (> 1000 users):
├── Bot: 1GB (Pro)
├── API: 2GB (Pro)
├── WebApp: 1GB (Pro)
└── Redis: 2GB (Pro)
```

## 🔄 CI/CD Pipeline

```
Developer → Git Push → GitHub
                          ↓
                    Railway Webhook
                          ↓
              ┌───────────┴───────────┐
              ▼                       ▼
        Build Services         Run Tests
              ↓                       ↓
        Deploy Services        Health Check
              ↓                       ↓
        Generate URLs          Update DNS
              ↓                       ↓
              └───────────┬───────────┘
                          ▼
                  Production Live
```

## 🌍 Domain Configuration

### Railway Domains (Automatic)

```
Bot Service:
└── No public URL needed

API Service:
└── api-production-xxxx.up.railway.app

WebApp Service:
└── webapp-production-xxxx.up.railway.app
```

### Custom Domains (Optional)

```
Your Domain → DNS Provider
                    ↓
            CNAME Records
                    ↓
        ┌───────────┴────────────┐
        ▼                        ▼
api.yourdomain.com    app.yourdomain.com
        │                        │
        ▼                        ▼
    API Service            WebApp Service
```

## 📈 Мониторинг

### Built-in Metrics (Railway)

```
Per Service:
├── CPU Usage
├── Memory Usage
├── Network I/O
├── Deployment History
└── Logs (real-time)
```

### External Monitoring (Recommended)

```
UptimeRobot:
├── API Health: /health (5 min interval)
└── WebApp: / (5 min interval)

Sentry (Error Tracking):
├── Bot errors
├── API errors
└── WebApp errors

Analytics:
└── WebApp: Vercel Analytics or Google Analytics
```

## 🔧 Обслуживание

### Обновление кода

```
1. Push to GitHub
2. Railway auto-deploys
3. Zero-downtime deployment
4. Health check passes
5. Traffic switches to new version
```

### Резервное копирование

```
Автоматически:
└── Railway Database Snapshots (для платных планов)

Вручную:
├── Export SQLite: scp bot.db local
└── Export Redis: SAVE command
```

## 🎯 Best Practices

### 1. Environment Variables
- ✅ Используйте `${{Service.VAR}}` для связи между сервисами
- ✅ Никогда не коммитьте секреты в Git
- ✅ Используйте Railway Secrets для чувствительных данных

### 2. Logging
- ✅ Structured logging (JSON format)
- ✅ Log levels: DEBUG, INFO, WARNING, ERROR
- ✅ Включите timestamp и context

### 3. Error Handling
- ✅ Graceful degradation
- ✅ Retry logic для внешних API
- ✅ User-friendly error messages

### 4. Performance
- ✅ Используйте Redis для кэширования
- ✅ Настройте CDN для статики (Cloudflare)
- ✅ Оптимизируйте изображения
- ✅ Используйте connection pooling

### 5. Security
- ✅ HTTPS everywhere
- ✅ Validate all inputs
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ Regular dependency updates

---

## 📚 Дополнительные ресурсы

- [Railway Documentation](https://docs.railway.app/)
- [Aiogram Documentation](https://docs.aiogram.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Архитектура обновлена:** 21.10.2025
