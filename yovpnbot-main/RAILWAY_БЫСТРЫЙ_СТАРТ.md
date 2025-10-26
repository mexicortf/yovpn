# ⚡ Быстрый старт: Развертывание YoVPN Bot на Railway

## 🎯 За 10 минут

Это краткая инструкция для опытных пользователей. Для подробного руководства см. [RAILWAY_ПОЛНОЕ_РУКОВОДСТВО.md](RAILWAY_ПОЛНОЕ_РУКОВОДСТВО.md)

---

## 📋 Что нужно подготовить

1. **Telegram Bot Token** - получите у [@BotFather](https://t.me/BotFather)
2. **Ваш Telegram ID** - узнайте у [@userinfobot](https://t.me/userinfobot)
3. **Marzban данные:**
   - API URL (например: `https://marzban.example.com`)
   - Username администратора
   - Password администратора
4. **GitHub аккаунт** - для форка репозитория
5. **Railway аккаунт** - зарегистрируйтесь на [railway.app](https://railway.app)

---

## 🚀 Шаги развертывания

### 1. Форк репозитория

```bash
# На GitHub
1. Перейдите: https://github.com/yourusername/yovpn-bot
2. Нажмите Fork
3. Дождитесь создания форка
```

### 2. Создание проекта на Railway

```bash
# На Railway
1. Откройте railway.app
2. Нажмите "+ New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите форкнутый репозиторий
```

### 3. Добавление базы данных

```bash
# В проекте Railway
1. Нажмите "+ New"
2. Database → Add MySQL
3. Нажмите "+ New"
4. Database → Add Redis (опционально)
```

### 4. Настройка Telegram Bot сервиса

```bash
# Переименуйте сервис в "telegram-bot"

# Settings → Deploy → Custom Start Command:
python -u bot/main.py

# Variables → добавьте:
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_TG_ID=your_telegram_id
SECRET_KEY=your_generated_secret_key
DATABASE_URL=${{MySQL.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
MARZBAN_API_URL=https://your-marzban.com
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=your_password
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

**Генерация SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Настройка Admin Panel сервиса

```bash
# В проекте нажмите "+ New" → GitHub Repo → yovpn-bot

# Переименуйте сервис в "admin-panel"

# Settings → Deploy → Custom Start Command:
uvicorn admin.main:app --host 0.0.0.0 --port $PORT

# Variables → добавьте:
ADMIN_TG_ID=your_telegram_id
SECRET_KEY=your_generated_secret_key
DATABASE_URL=${{MySQL.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
ADMIN_HOST=0.0.0.0
ADMIN_PORT=$PORT

# Settings → Networking → Generate Domain
# Сохраните полученный URL
```

### 6. Применение миграций

```bash
# В проекте нажмите "+ New" → GitHub Repo → yovpn-bot

# Переименуйте сервис в "migrations"

# Settings → Deploy → Custom Start Command:
alembic upgrade head

# Variables:
DATABASE_URL=${{MySQL.DATABASE_URL}}

# После успешного выполнения удалите этот сервис
```

### 7. Проверка работы

```bash
# Telegram Bot
1. Найдите бота в Telegram
2. Отправьте /start
3. Должен прийти приветственный бонус

# Admin Panel
1. Откройте сгенерированный URL
2. Должна открыться админ панель
3. Проверьте статистику
```

---

## 📊 Структура проекта на Railway

После развертывания у вас будет 3 активных сервиса:

```
yovpn-production (проект)
├── MySQL (база данных)
├── Redis (кэш)
├── telegram-bot (Telegram бот)
└── admin-panel (админ панель)
```

---

## 🔧 Основные команды Railway CLI

```bash
# Установка
npm install -g @railway/cli

# Авторизация
railway login

# Подключение к проекту
railway link

# Просмотр логов
railway logs --service telegram-bot --tail

# Выполнение команд
railway run alembic upgrade head

# Подключение к MySQL
railway connect MySQL
```

---

## ⚙️ Переменные окружения (полный список)

### Обязательные для Telegram Bot

| Переменная | Пример значения |
|-----------|----------------|
| `TELEGRAM_BOT_TOKEN` | `123456789:ABCdef...` |
| `ADMIN_TG_ID` | `7610842643` |
| `SECRET_KEY` | `генерируемый_ключ_32+_символа` |
| `DATABASE_URL` | `${{MySQL.DATABASE_URL}}` |
| `MARZBAN_API_URL` | `https://marzban.example.com` |
| `MARZBAN_USERNAME` | `admin` |
| `MARZBAN_PASSWORD` | `your_password` |

### Обязательные для Admin Panel

| Переменная | Пример значения |
|-----------|----------------|
| `ADMIN_TG_ID` | `7610842643` |
| `SECRET_KEY` | `тот_же_что_в_боте` |
| `DATABASE_URL` | `${{MySQL.DATABASE_URL}}` |
| `ADMIN_HOST` | `0.0.0.0` |
| `ADMIN_PORT` | `$PORT` |

### Опциональные

| Переменная | Значение по умолчанию |
|-----------|----------------------|
| `REDIS_URL` | `${{Redis.REDIS_URL}}` |
| `PYTHONUNBUFFERED` | `1` |
| `PYTHONDONTWRITEBYTECODE` | `1` |
| `DEBUG` | `False` |
| `LOG_LEVEL` | `INFO` |
| `DAILY_PRICE` | `4.0` |
| `WELCOME_BONUS` | `12.0` |
| `REFERRAL_BONUS` | `8.0` |
| `MIN_DEPOSIT` | `40.0` |
| `SUPPORT_USERNAME` | `@YoVPNSupport` |
| `CHANNEL_USERNAME` | `@yodevelop` |

---

## 🐛 Быстрое устранение неполадок

### Бот не отвечает
```bash
# Проверьте логи
railway logs --service telegram-bot --tail

# Проверьте статус
railway status

# Перезапустите
railway redeploy --service telegram-bot
```

### Админ панель не открывается
```bash
# Проверьте, что домен сгенерирован
Settings → Networking → Generate Domain

# Проверьте логи
railway logs --service admin-panel --tail

# Проверьте порт
Variables → ADMIN_PORT должен быть $PORT
```

### Ошибка подключения к БД
```bash
# Проверьте статус MySQL
railway status

# Проверьте DATABASE_URL
railway variables --service telegram-bot

# Примените миграции
railway run alembic upgrade head
```

### Ошибка Marzban API
```bash
# Проверьте переменные
railway variables --service telegram-bot | grep MARZBAN

# Проверьте доступность Marzban
curl https://your-marzban.com

# Проверьте формат URL (с https://)
```

---

## 📈 Мониторинг

### Просмотр метрик

```bash
Railway Dashboard → Сервис → Metrics
- CPU Usage
- Memory Usage
- Network Traffic
```

### Настройка алертов

Рекомендуется использовать:
- **UptimeRobot** - [uptimerobot.com](https://uptimerobot.com) (бесплатно)
- **BetterUptime** - [betteruptime.com](https://betteruptime.com) (бесплатно)

---

## 💰 Стоимость

### Hobby Plan (Бесплатно)
- $5 кредитов в месяц
- 512MB RAM на сервис
- Подходит для малых ботов (до 100 пользователей)

**Примерное использование:**
- MySQL: ~$1-2/месяц
- Redis: ~$0.5-1/месяц
- Bot: ~$1-2/месяц
- Admin: ~$1-2/месяц
- **Итого:** ~$4-7/месяц

### Developer Plan ($5/месяц)
- $5 кредитов включено + доп. использование
- 8GB RAM на сервис
- Подходит для средних ботов (100-1000 пользователей)

---

## 📚 Дополнительные ресурсы

- **Подробное руководство:** [RAILWAY_ПОЛНОЕ_РУКОВОДСТВО.md](RAILWAY_ПОЛНОЕ_РУКОВОДСТВО.md)
- **Railway Docs:** [docs.railway.app](https://docs.railway.app)
- **Aiogram Docs:** [docs.aiogram.dev](https://docs.aiogram.dev)
- **FastAPI Docs:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

## ✅ Чеклист

- [ ] Получен токен бота от BotFather
- [ ] Сгенерирован SECRET_KEY
- [ ] Форкнут репозиторий на GitHub
- [ ] Создан проект на Railway
- [ ] Добавлена база данных MySQL
- [ ] Добавлен Redis (опционально)
- [ ] Настроен сервис telegram-bot
- [ ] Настроен сервис admin-panel
- [ ] Применены миграции базы данных
- [ ] Бот отвечает на /start
- [ ] Админ панель открывается
- [ ] Подключение к Marzban работает

---

## 🎉 Готово!

После выполнения всех шагов у вас будет полностью рабочий VPN бот на Railway.

**Следующие шаги:**
1. Настройте команды бота в BotFather
2. Настройте меню и описание
3. Добавьте аватар бота
4. Настройте платежную систему
5. Запускайте и зарабатывайте! 💰

---

**Нужна помощь?**
- 📖 [Подробное руководство](RAILWAY_ПОЛНОЕ_РУКОВОДСТВО.md)
- 🐛 [GitHub Issues](https://github.com/yourusername/yovpn-bot/issues)
- 💬 [Telegram Support](https://t.me/YoVPNSupport)

---

**Создано с ❤️ для YoVPN Bot**
