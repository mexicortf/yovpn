# YoVPN WebApp API 🚀

FastAPI backend для YoVPN WebApp - обработка подписок, валидация Telegram данных, генерация URI.

## ✨ Особенности

- ⚡ **FastAPI** - Высокая производительность
- 🔐 **Telegram валидация** - HMAC подпись проверка
- 📊 **Интеграция с Marzban** - Получение подписок
- 🔄 **CORS** - Поддержка кросс-доменных запросов
- 📝 **OpenAPI Docs** - Автоматическая документация

## 🏗️ Архитектура

```
api/
├── app/
│   ├── routes/          # API эндпоинты
│   │   └── api.py
│   ├── models/          # Pydantic схемы
│   │   └── schemas.py
│   ├── services/        # Бизнес-логика
│   │   └── subscription_service.py
│   ├── utils/           # Утилиты
│   │   └── telegram.py
│   ├── config.py        # Конфигурация
│   └── main.py          # FastAPI приложение
├── requirements.txt
└── .env
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd api
pip install -r requirements.txt
```

### 2. Настройка окружения

Создайте файл `.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Security
SECRET_KEY=your-super-secret-key

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

# Marzban
MARZBAN_API_URL=http://localhost:8080
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=admin

# Download URLs
ANDROID_APK_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-android.apk
IOS_APP_STORE_URL=https://apps.apple.com/app/v2raytun
MACOS_DMG_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-macos.dmg
WINDOWS_EXE_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-windows.exe
ANDROID_TV_APK_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-tv.apk
```

### 3. Запуск сервера

```bash
# Development
python -m app.main

# или с uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: http://localhost:8000

### 4. Документация API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "YoVPN WebApp API"
}
```

### Validate Telegram Data

```http
POST /api/validate
Content-Type: application/json

{
  "init_data": "telegram_init_data_string"
}
```

**Response:**
```json
{
  "valid": true,
  "user_id": 123456789
}
```

### Get Subscription

```http
GET /api/subscription/123456789
X-Telegram-Init-Data: telegram_init_data_string
```

**Response:**
```json
{
  "user_id": 123456789,
  "subscription_uri": "v2ray://...",
  "expires_at": "2025-12-31T23:59:59",
  "is_active": true,
  "subscription_type": "premium"
}
```

### Get Latest Version

```http
GET /api/version/android
```

**Response:**
```json
{
  "platform": "android",
  "version": "latest",
  "download_url": "https://github.com/.../v2raytun-android.apk"
}
```

### Track Activation

```http
POST /api/track/activation
Content-Type: application/json
X-Telegram-Init-Data: telegram_init_data_string

{
  "user_id": 123456789,
  "platform": "android"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Activation tracked successfully"
}
```

## 🔐 Безопасность

### Telegram Init Data Validation

API использует HMAC-SHA256 для валидации данных от Telegram:

```python
from app.utils.telegram import validate_telegram_init_data

is_valid, parsed_data = validate_telegram_init_data(init_data)
```

### CORS

CORS настроен для защиты от неавторизованных доменов:

```python
CORS_ORIGINS=http://localhost:3000,https://your-webapp.com
```

## 🔗 Интеграция с Marzban

API использует существующий `MarzbanService` из бота:

```python
from bot.services.marzban_service import MarzbanService

marzban = MarzbanService()
subscription = await marzban.get_user_subscription(username)
```

## 📊 Мониторинг

### Логирование

API логирует все запросы и ошибки:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Метрики

Можно добавить интеграцию с Prometheus/Grafana для мониторинга.

## 🚀 Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    env_file:
      - ./api/.env
    restart: unless-stopped
```

### Nginx Reverse Proxy

```nginx
location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 🧪 Тестирование

```bash
# Установка dev зависимостей
pip install pytest pytest-asyncio httpx

# Запуск тестов
pytest
```

## 📄 Лицензия

MIT
