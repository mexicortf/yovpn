# Railway Configuration Files

Эти конфигурационные файлы помогут вам быстро настроить сервисы на Railway.

## Структура файлов

- `bot.railway.json` - конфигурация для Telegram бота
- `api.railway.json` - конфигурация для API backend
- `webapp.railway.json` - конфигурация для WebApp frontend

## Использование

### Автоматическая настройка

Railway автоматически обнаружит эти конфигурации при деплое из репозитория.

### Ручная настройка

Если автоматическая настройка не работает, используйте эти файлы как справочник для ручной настройки каждого сервиса в Railway Dashboard.

## Порядок создания сервисов

1. **Redis** (база данных)
2. **telegram-bot** (используйте `bot.railway.json`)
3. **api** (используйте `api.railway.json`)
4. **webapp** (используйте `webapp.railway.json`)

## Важные замечания

### Для bot:
- Dockerfile находится в корне проекта
- Start command: `python bot/main.py`
- Не требует публичного URL

### Для api:
- Root Directory: `api`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Требуется публичный URL** (Generate Domain)

### Для webapp:
- Root Directory: `webapp`
- Start command: `npm start`
- **Требуется публичный URL** (Generate Domain)

## Environment Variables

Все необходимые переменные окружения описаны в каждом `.railway.json` файле в секции `env`.

### Критические переменные (требуют ручной настройки):

1. `TELEGRAM_BOT_TOKEN` - получите от @BotFather
2. `SECRET_KEY` - сгенерируйте: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
3. `MARZBAN_API_URL` - URL вашего Marzban сервера
4. `MARZBAN_USERNAME` - имя администратора Marzban
5. `MARZBAN_PASSWORD` - пароль администратора Marzban

### Автоматические переменные:

- `${{Redis.REDIS_URL}}` - автоматически заполняется при добавлении Redis
- `$PORT` - автоматически предоставляется Railway

## Настройка CORS

После создания webapp сервиса и генерации его URL, обновите в api сервисе:

```env
CORS_ORIGINS=https://webapp-production-xxxx.up.railway.app
```

## Связь между сервисами

```
Telegram Bot ──┐
               ├──> Redis (кэширование)
API Backend ───┘
               
WebApp Frontend ──> API Backend (HTTPS)
```

## Troubleshooting

Если сервис не запускается, проверьте:

1. **Логи** в Railway Dashboard → Logs
2. **Root Directory** для api и webapp
3. **Start Command** соответствует файлу конфигурации
4. **Все обязательные env переменные** установлены
5. **Dockerfile** существует в нужной директории

## Дополнительно

Полную инструкцию по деплою смотрите в `RAILWAY_DEPLOYMENT_GUIDE.md` в корне проекта.
