# ✅ Чеклист для деплоя YoVPN на Railway

## 📋 Быстрый старт

### 1️⃣ Подготовка (5 минут)

- [ ] Создал бота через [@BotFather](https://t.me/BotFather)
- [ ] Сохранил **TELEGRAM_BOT_TOKEN**: `_______________`
- [ ] Сгенерировал **SECRET_KEY**: 
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  Ключ: `_______________`
- [ ] Получил данные Marzban:
  - URL: `_______________`
  - Username: `_______________`
  - Password: `_______________`

### 2️⃣ Railway Setup (10 минут)

- [ ] Зарегистрировался на [railway.app](https://railway.app)
- [ ] Создал новый проект "Deploy from GitHub repo"
- [ ] Выбрал репозиторий YoVPN

### 3️⃣ Создание сервисов

#### Redis
- [ ] Добавил: "+ New" → "Database" → "Redis"

#### Telegram Bot
- [ ] Добавил: "+ New" → "Empty Service" → название "telegram-bot"
- [ ] Настроил:
  - Start Command: `python bot/main.py`
- [ ] Добавил переменные:
  ```env
  TELEGRAM_BOT_TOKEN=
  MARZBAN_API_URL=
  MARZBAN_USERNAME=
  MARZBAN_PASSWORD=
  SECRET_KEY=
  REDIS_URL=${{Redis.REDIS_URL}}
  SQLALCHEMY_DATABASE_URL=sqlite:///data/bot.db
  PYTHONUNBUFFERED=1
  ```

#### API Backend
- [ ] Добавил: "+ New" → "Empty Service" → название "api"
- [ ] Настроил:
  - Root Directory: `api`
  - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Добавил переменные:
  ```env
  TELEGRAM_BOT_TOKEN=
  SECRET_KEY=
  MARZBAN_API_URL=
  MARZBAN_USERNAME=
  MARZBAN_PASSWORD=
  CORS_ORIGINS=*
  REDIS_URL=${{Redis.REDIS_URL}}
  API_HOST=0.0.0.0
  API_PORT=$PORT  # Railway's PORT variable will be automatically used
  ```
- [ ] Сгенерировал публичный URL: Settings → Networking → "Generate Domain"
- [ ] Сохранил API URL: `_______________`

#### WebApp Frontend
- [ ] Добавил: "+ New" → "Empty Service" → название "webapp"
- [ ] Настроил:
  - Root Directory: `webapp`
  - Build Command: `npm install && npm run build`
  - Start Command: `npm start`
- [ ] Добавил переменные:
  ```env
  NODE_ENV=production
  NEXT_PUBLIC_TELEGRAM_BOT_TOKEN=
  NEXT_PUBLIC_API_BASE_URL=[API URL из предыдущего шага]
  NEXT_PUBLIC_BASE_URL=[будет после генерации домена]
  NEXT_PUBLIC_DEV_MODE=false
  ```
- [ ] Сгенерировал публичный URL: Settings → Networking → "Generate Domain"
- [ ] Сохранил WebApp URL: `_______________`
- [ ] Обновил переменную `NEXT_PUBLIC_BASE_URL` этим URL

### 4️⃣ Финальная настройка (5 минут)

- [ ] Обновил CORS в API сервисе:
  ```env
  CORS_ORIGINS=[WebApp URL]
  ```
- [ ] Настроил Menu Button в [@BotFather](https://t.me/BotFather):
  - `/mybots` → выбрал бота
  - "Bot Settings" → "Menu Button"
  - Ввел WebApp URL

### 5️⃣ Проверка (5 минут)

- [ ] API работает:
  ```bash
  curl [API URL]/docs
  ```
- [ ] WebApp загружается в браузере: `[WebApp URL]`
- [ ] Бот отвечает на `/start` в Telegram
- [ ] Все сервисы показывают статус "Active" в Railway

### 6️⃣ Мониторинг (опционально)

- [ ] Настроил uptime monitoring на [uptimerobot.com](https://uptimerobot.com)
  - Monitor URL: `[API URL]/health`
- [ ] Настроил error tracking на [sentry.io](https://sentry.io)

---

## 🔥 Быстрая настройка переменных

### Бот (telegram-bot)
```env
TELEGRAM_BOT_TOKEN=
MARZBAN_API_URL=
MARZBAN_USERNAME=
MARZBAN_PASSWORD=
SECRET_KEY=
REDIS_URL=${{Redis.REDIS_URL}}
SQLALCHEMY_DATABASE_URL=sqlite:///data/bot.db
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

### API (api)
```env
TELEGRAM_BOT_TOKEN=
SECRET_KEY=
MARZBAN_API_URL=
MARZBAN_USERNAME=
MARZBAN_PASSWORD=
CORS_ORIGINS=https://webapp-production-xxxx.up.railway.app
REDIS_URL=${{Redis.REDIS_URL}}
API_HOST=0.0.0.0
API_PORT=$PORT  # Railway's PORT variable will be automatically used
```

### WebApp (webapp)
```env
NODE_ENV=production
NEXT_PUBLIC_TELEGRAM_BOT_TOKEN=
NEXT_PUBLIC_API_BASE_URL=https://api-production-xxxx.up.railway.app
NEXT_PUBLIC_BASE_URL=https://webapp-production-xxxx.up.railway.app
NEXT_PUBLIC_DEV_MODE=false
NEXT_PUBLIC_ANDROID_APK_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-android.apk
NEXT_PUBLIC_IOS_APP_STORE_URL=https://apps.apple.com/app/v2raytun
NEXT_PUBLIC_MACOS_DMG_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-macos.dmg
NEXT_PUBLIC_WINDOWS_EXE_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-windows.exe
NEXT_PUBLIC_ANDROID_TV_APK_URL=https://github.com/yovpn/v2raytun/releases/latest/download/v2raytun-tv.apk
```

---

## 🐛 Частые проблемы

### Бот не отвечает
✅ Проверьте логи в Railway → telegram-bot → Logs
✅ Убедитесь, что токен корректный
✅ Проверьте, что сервис показывает "Active"

### WebApp не загружается
✅ Проверьте `NEXT_PUBLIC_API_BASE_URL` - должен быть URL API
✅ Проверьте `CORS_ORIGINS` в API - должен содержать URL WebApp
✅ Проверьте логи webapp сервиса

### API не отвечает
✅ Проверьте логи API сервиса
✅ Убедитесь, что порт установлен как `$PORT`
✅ Проверьте health endpoint: `curl [API URL]/health`

---

## 📊 Итого

**Время деплоя**: ~25 минут
**Стоимость**: $0-5/месяц на Railway
**Сервисы**: 4 (Redis + Bot + API + WebApp)

---

**Готово! 🎉** Ваш YoVPN бот работает в production!
