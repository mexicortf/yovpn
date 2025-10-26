# 🎯 Railway Шпаргалка: Команды и настройки

## ⚡ Быстрый доступ к командам и настройкам

---

## 📋 Переменные окружения

### Telegram Bot Service

```env
# Обязательные
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
ADMIN_TG_ID=7610842643
SECRET_KEY=ваш_сгенерированный_ключ_32_символа
DATABASE_URL=${{MySQL.DATABASE_URL}}
MARZBAN_API_URL=https://marzban.example.com
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=your_password

# Опциональные
REDIS_URL=${{Redis.REDIS_URL}}
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
DEBUG=False
LOG_LEVEL=INFO

# Экономика
DAILY_PRICE=4.0
WELCOME_BONUS=12.0
REFERRAL_BONUS=8.0
MIN_DEPOSIT=40.0

# Контакты
SUPPORT_USERNAME=@YoVPNSupport
CHANNEL_USERNAME=@yodevelop
```

### Admin Panel Service

```env
# Обязательные
ADMIN_TG_ID=7610842643
SECRET_KEY=тот_же_что_и_в_боте
DATABASE_URL=${{MySQL.DATABASE_URL}}
ADMIN_HOST=0.0.0.0
ADMIN_PORT=$PORT

# Опциональные
REDIS_URL=${{Redis.REDIS_URL}}
MARZBAN_API_URL=https://marzban.example.com
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=your_password
```

---

## 🚀 Команды запуска

### Telegram Bot
```bash
python -u bot/main.py
```

### Admin Panel
```bash
uvicorn admin.main:app --host 0.0.0.0 --port $PORT
```

### Миграции
```bash
alembic upgrade head
```

---

## 🛠️ Railway CLI

### Установка
```bash
npm install -g @railway/cli
```

### Авторизация
```bash
railway login
```

### Подключение к проекту
```bash
railway link
```

### Просмотр логов
```bash
# Все логи
railway logs

# Логи конкретного сервиса
railway logs --service telegram-bot

# Следить за логами в реальном времени
railway logs --service telegram-bot --tail

# Последние 100 строк
railway logs --tail 100
```

### Управление переменными
```bash
# Просмотр всех переменных
railway variables

# Установка переменной
railway variables set KEY=value

# Удаление переменной
railway variables delete KEY

# Переменные конкретного сервиса
railway variables --service telegram-bot
```

### Выполнение команд
```bash
# Выполнить команду в Railway окружении
railway run python manage.py

# Применить миграции
railway run alembic upgrade head

# Запустить скрипт
railway run python scripts/seed_data.py
```

### Подключение к базе данных
```bash
# Подключиться к MySQL
railway connect MySQL

# Подключиться к Redis
railway connect Redis
```

### Управление проектом
```bash
# Статус проекта
railway status

# Информация о проекте
railway whoami

# Список окружений
railway environment

# Открыть проект в браузере
railway open
```

### Развертывание
```bash
# Загрузить код на Railway
railway up

# Редеплой сервиса
railway redeploy --service telegram-bot

# Откат к предыдущей версии
railway rollback
```

---

## 🗄️ MySQL команды

### Подключение
```bash
railway connect MySQL
```

### Основные команды SQL
```sql
-- Показать все базы данных
SHOW DATABASES;

-- Использовать базу данных
USE railway;

-- Показать таблицы
SHOW TABLES;

-- Показать структуру таблицы
DESCRIBE users;

-- Просмотр данных
SELECT * FROM users LIMIT 10;

-- Количество пользователей
SELECT COUNT(*) FROM users;

-- Количество активных подписок
SELECT COUNT(*) FROM subscriptions WHERE is_active = 1;

-- Общий баланс пользователей
SELECT SUM(balance) FROM users;

-- Последние транзакции
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;

-- Пользователи с положительным балансом
SELECT * FROM users WHERE balance > 0;

-- Резервная копия (экспорт)
-- Выполнить в терминале, не в MySQL
mysqldump -h host -u user -p database > backup.sql

-- Восстановление (импорт)
mysql -h host -u user -p database < backup.sql
```

---

## 🔄 Redis команды

### Подключение
```bash
railway connect Redis
```

### Основные команды Redis
```redis
# Проверка подключения
PING

# Просмотр всех ключей
KEYS *

# Получить значение
GET key_name

# Установить значение
SET key_name value

# Установить значение с TTL (время жизни в секундах)
SETEX key_name 3600 value

# Удалить ключ
DEL key_name

# Время жизни ключа
TTL key_name

# Информация о Redis
INFO

# Очистить все данные (осторожно!)
FLUSHALL

# Количество ключей в базе
DBSIZE

# Выход
EXIT
```

---

## 🐛 Диагностика

### Проверка статуса сервисов
```bash
# Статус всех сервисов
railway status

# Логи с ошибками
railway logs | grep ERROR

# Логи с предупреждениями
railway logs | grep WARNING
```

### Проверка подключения к базе данных
```bash
# В Railway CLI
railway run python -c "from database.db import engine; print('OK' if engine else 'FAIL')"
```

### Проверка переменных окружения
```bash
# Показать все переменные
railway variables

# Проверка конкретной переменной
railway variables | grep DATABASE_URL
```

### Тест Marzban API
```bash
# Выполнить в Railway окружении
railway run python -c "
import aiohttp
import asyncio
async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://your-marzban.com/api/admin') as resp:
            print(resp.status)
asyncio.run(test())
"
```

---

## 📊 Мониторинг

### Railway Dashboard
```
URL: https://railway.app/dashboard
Путь: Project → Service → Metrics

Метрики:
- CPU Usage
- Memory Usage
- Network (In/Out)
- Build Time
- Restart Count
```

### Внешний мониторинг

#### UptimeRobot
```
URL: https://uptimerobot.com
Настройка:
1. Add New Monitor
2. Monitor Type: HTTP(s)
3. URL: https://admin-panel-xxxx.up.railway.app/admin
4. Monitoring Interval: 5 minutes
```

#### BetterUptime
```
URL: https://betteruptime.com
Настройка:
1. Create Monitor
2. URL: https://admin-panel-xxxx.up.railway.app
3. Check interval: 1 minute
4. Notifications: Telegram/Email
```

---

## 🔐 Безопасность

### Генерация SECRET_KEY
```bash
# Linux/Mac
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Windows
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Онлайн (32 символа)
https://www.random.org/strings/
```

### Проверка секретов
```bash
# Проверить, что нет секретов в коде
git grep -i "password\|secret\|token" | grep -v ".env\|.md"

# Проверить .env не в git
git ls-files | grep .env
# Должен вернуть пустой результат
```

### Обновление токена бота
```bash
# 1. Получите новый токен у BotFather
# 2. Обновите в Railway
railway variables set TELEGRAM_BOT_TOKEN=новый_токен

# 3. Перезапустите сервис
railway redeploy --service telegram-bot
```

---

## 🔄 Обновление приложения

### Автоматическое (через GitHub)
```bash
# Локально
git add .
git commit -m "Update: описание изменений"
git push origin main

# Railway автоматически задеплоит изменения
```

### Ручное
```bash
# Railway Dashboard
1. Откройте сервис
2. Deployments → Redeploy
```

### Откат к предыдущей версии
```bash
# Railway Dashboard
1. Откройте сервис
2. Deployments
3. Найдите успешный деплой
4. Нажмите "..." → Redeploy

# Или через CLI
railway rollback
```

---

## 🗂️ Миграции базы данных

### Создание миграции
```bash
# Локально
alembic revision --autogenerate -m "Описание изменений"

# Результат: новый файл в database/migrations/versions/
```

### Применение миграций
```bash
# Через Railway CLI
railway run alembic upgrade head

# Или создайте временный сервис миграций
Start Command: alembic upgrade head
Variables: DATABASE_URL=${{MySQL.DATABASE_URL}}
```

### Откат миграции
```bash
# Откатить одну миграцию
railway run alembic downgrade -1

# Откатить к конкретной версии
railway run alembic downgrade <revision_id>
```

### История миграций
```bash
railway run alembic history

# Текущая версия
railway run alembic current
```

---

## 📦 Управление зависимостями

### Обновление зависимостей
```bash
# Локально
pip install --upgrade package_name

# Сохранить в requirements.txt
pip freeze > requirements.txt

# Коммит и push
git add requirements.txt
git commit -m "Update dependencies"
git push

# Railway автоматически установит новые зависимости
```

### Проверка версий
```bash
# Локально
pip list

# В Railway
railway run pip list
```

---

## 🎛️ Настройки Railway

### Сервис Settings

#### General
```
Service Name: telegram-bot / admin-panel
```

#### Deploy
```
Build Command: (пусто)
Start Command: python -u bot/main.py
Restart Policy: On Failure
Health Check: (пусто, автоматически)
```

#### Networking
```
Generate Domain: [Кнопка для генерации]
Custom Domain: [Опционально]
```

#### Variables
```
См. раздел "Переменные окружения" выше
```

---

## 📱 Telegram Bot настройки

### BotFather команды
```
/mybots - Список ваших ботов
/setcommands - Установить команды
/setdescription - Установить описание
/setabouttext - Установить краткое описание
/setuserpic - Установить аватар
/setname - Изменить имя
/setprivacy - Настройки приватности
/deletebot - Удалить бота
```

### Команды бота для пользователей
```
start - Запустить бота
help - Помощь
balance - Мой баланс
subscription - Моя подписка
referral - Реферальная программа
support - Поддержка
```

### Команды бота для администратора
```
admin - Админ панель
admin_stats - Быстрая статистика
admin_users - Управление пользователями
```

---

## 🔍 Troubleshooting быстро

### Бот не отвечает
```bash
railway status
railway logs --service telegram-bot --tail
railway redeploy --service telegram-bot
```

### Админ панель не работает
```bash
railway logs --service admin-panel --tail
# Проверить: ADMIN_PORT=$PORT
# Проверить: Start Command содержит --port $PORT
railway redeploy --service admin-panel
```

### База данных недоступна
```bash
railway status
railway connect MySQL
# Если подключение работает, проверить DATABASE_URL
railway variables | grep DATABASE_URL
```

### Marzban не подключается
```bash
# Проверить URL
curl https://your-marzban.com

# Проверить переменные
railway variables | grep MARZBAN

# Тест из Railway
railway run python -c "import requests; print(requests.get('https://your-marzban.com').status_code)"
```

---

## 📞 Контакты поддержки

### Railway Support
- 📧 Email: team@railway.app
- 💬 Discord: https://discord.gg/railway
- 📖 Docs: https://docs.railway.app

### YoVPN Bot Support
- 💬 Telegram: @YoVPNSupport
- 📱 Channel: @yodevelop
- 🐛 GitHub: github.com/yourusername/yovpn-bot/issues

---

## ✅ Чеклист проверки

```bash
# База данных
railway status  # MySQL должен быть Active
railway connect MySQL  # Должно подключиться

# Бот
railway logs --service telegram-bot | grep "Бот запущен"
# Отправить /start боту в Telegram

# Админ панель
curl https://admin-panel-xxxx.up.railway.app/admin
# Должен вернуть 200 OK

# Переменные
railway variables | wc -l
# Должно быть минимум 10 переменных
```

---

**Сохраните эту шпаргалку для быстрого доступа!**

*Последнее обновление: 24 октября 2025*
