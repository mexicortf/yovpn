# Переменные окружения для Railway

## Проблема с MARZBAN_API_URL

Если вы видите предупреждение "⚠️ Marzban API URL не настроен" в логах Railway, проверьте следующее:

## Обязательные переменные окружения для бота

Убедитесь, что в настройках вашего Railway проекта добавлены следующие переменные:

### 1. TELEGRAM_BOT_TOKEN
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
```
Получите токен у @BotFather в Telegram

**Важно:** Используйте именно `TELEGRAM_BOT_TOKEN`, а не `USERBOT_TOKEN` (старое название)

### 2. MARZBAN_API_URL
```
MARZBAN_API_URL=https://your-marzban-server.com/api
```
Полный URL вашего Marzban API сервера с протоколом `https://` или `http://`

**Важные моменты:**
- URL должен быть **полным** (с `https://` или `http://`)
- URL должен быть **доступен** из интернета (если Railway развернут в облаке)
- Проверьте, что URL **не содержит лишних пробелов** в начале или конце
- URL должен заканчиваться на `/api` если ваш Marzban использует этот префикс

### 3. MARZBAN_ADMIN_TOKEN
```
MARZBAN_ADMIN_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
Токен администратора Marzban API

**Как получить токен:**
1. Откройте панель Marzban
2. Войдите под учетной записью администратора
3. Перейдите в настройки профиля
4. Скопируйте API токен

**Альтернатива:** Вместо токена можно использовать логин/пароль:
```
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=your_password
```

### 4. SECRET_KEY
```
SECRET_KEY=your-secret-key-min-32-characters-long
```
Секретный ключ для шифрования данных (минимум 32 символа)

Сгенерируйте с помощью:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Опциональные переменные

### REDIS_URL
```
REDIS_URL=${{Redis.REDIS_URL}}
```
Если используете Railway Redis, эта переменная подставится автоматически

### SQLALCHEMY_DATABASE_URL
```
SQLALCHEMY_DATABASE_URL=sqlite:///data/bot.db
```
По умолчанию используется SQLite

## Как проверить переменные на Railway

1. Зайдите в ваш проект на Railway
2. Откройте настройки сервиса "telegram-bot"
3. Перейдите во вкладку "Variables"
4. Убедитесь, что все переменные **точно** названы как указано выше
5. Проверьте, что значения **не содержат лишних пробелов**

## Проверка после развертывания

После добавления переменных:

1. Сохраните изменения в Railway
2. Railway автоматически перезапустит сервис
3. Проверьте логи (Deployments → Latest → View Logs)
4. Вы должны увидеть:
   ```
   ✅ MarzbanService инициализирован: https://your-marzban-server.com/api
   ✅ Marzban API доступен
   ```

Если всё равно видите предупреждение, проверьте:
- Доступность Marzban сервера из интернета
- Правильность токена администратора
- Отсутствие файрвола/VPN блокирующего доступ

## Миграция со старых названий переменных

Если ранее использовали `USERBOT_TOKEN`, переименуйте на `TELEGRAM_BOT_TOKEN`:

**Старое (не рекомендуется):**
```
USERBOT_TOKEN=123456789:ABC...
```

**Новое (рекомендуется):**
```
TELEGRAM_BOT_TOKEN=123456789:ABC...
```

Код поддерживает оба варианта для обратной совместимости, но рекомендуется использовать `TELEGRAM_BOT_TOKEN`.
