# ⚡ YoVPN WebApp - Quick Start

Быстрое руководство для запуска YoVPN WebApp за 5 минут.

---

## 🎯 Что вы получите

После выполнения этих шагов у вас будет:

✅ Работающий Telegram WebApp на http://localhost:3000  
✅ API Backend на http://localhost:8000  
✅ Полная интеграция с вашим Telegram ботом  
✅ Режим разработчика для тестирования  

---

## 📋 Требования

Убедитесь, что установлено:

- ✅ **Node.js 18+** ([Скачать](https://nodejs.org/))
- ✅ **Python 3.11+** ([Скачать](https://www.python.org/))
- ✅ **npm** (устанавливается с Node.js)
- ✅ **Git** (опционально)

Проверка:
```bash
node --version  # v18.0.0 или выше
python3 --version  # Python 3.11 или выше
npm --version  # 9.0.0 или выше
```

---

## 🚀 Запуск за 5 минут

### Вариант 1: Автоматический запуск (Рекомендуется)

```bash
# 1. Перейдите в директорию проекта
cd /workspace

# 2. Запустите скрипт
./start-webapp.sh

# Готово! 🎉
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Вариант 2: Ручной запуск

#### Терминал 1 - Frontend

```bash
cd webapp
npm install
npm run dev
```

#### Терминал 2 - Backend

```bash
cd api
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

---

## ✅ Проверка работы

### 1. Откройте Frontend

```
http://localhost:3000
```

Вы должны увидеть:
- 🎨 Красивый UI с glassmorphism
- 📱 Иконки платформ (Android, iOS, macOS, Windows, TV)
- 🛠️ Кнопка Dev Mode в правом нижнем углу

### 2. Откройте API Docs

```
http://localhost:8000/docs
```

Вы должны увидеть:
- 📚 Swagger UI с документацией API
- 🔌 Все endpoints (/api/health, /api/subscription, etc.)

### 3. Проверьте Health Check

```bash
curl http://localhost:8000/api/health
```

Ответ:
```json
{
  "status": "healthy",
  "service": "YoVPN WebApp API"
}
```

---

## 🛠️ Режим разработчика

### Активация

1. Откройте http://localhost:3000
2. Нажмите кнопку 🛠️ в правом нижнем углу
3. Введите данные:
   - **Mock User ID**: `123456789`
   - **Mock Subscription URI**: `v2ray://test-subscription-uri`
4. Нажмите **Save Settings**

### Тестирование

Теперь можете протестировать все 3 шага:

1. **Шаг 1**: Выберите любую платформу (например, Android)
2. **Шаг 2**: Нажмите "Скачать приложение"
3. **Шаг 3**: Нажмите "Активировать подписку"

Всё должно работать без реального Telegram!

---

## 🔗 Интеграция с Telegram Bot

### 1. Обновите URL в боте

Откройте `bot/handlers/webapp_handler.py`:

```python
# Для локальной разработки через ngrok:
WEBAPP_URL = "https://abc123.ngrok.io"

# Для production:
# WEBAPP_URL = "https://yourdomain.com"
```

### 2. Зарегистрируйте handler

В `bot/main.py` добавьте:

```python
from bot.handlers import webapp_handler

# Регистрация роутера
dp.include_router(webapp_handler.router)
```

### 3. Локальное тестирование через ngrok

```bash
# Установите ngrok
npm install -g ngrok

# Запустите туннель
ngrok http 3000

# Скопируйте URL (например, https://abc123.ngrok.io)
# Обновите WEBAPP_URL в bot/handlers/webapp_handler.py
```

### 4. Запустите бота

```bash
python bot/main.py
```

### 5. Тестирование в Telegram

1. Откройте бота в Telegram
2. Отправьте команду `/webapp`
3. Нажмите кнопку "🚀 Открыть WebApp"
4. WebApp откроется прямо в Telegram!

---

## 📝 Настройка переменных окружения

### Frontend (.env.local)

Файл уже создан в `webapp/.env.local` со значениями по умолчанию.

Измените при необходимости:

```env
# Режим разработки
NEXT_PUBLIC_DEV_MODE=true

# API URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Telegram Bot Token
NEXT_PUBLIC_TELEGRAM_BOT_TOKEN=your_bot_token_here

# Download URLs (замените на актуальные)
NEXT_PUBLIC_ANDROID_APK_URL=https://github.com/.../v2raytun-android.apk
NEXT_PUBLIC_IOS_APP_STORE_URL=https://apps.apple.com/app/v2raytun
# ... и т.д.
```

### Backend (.env)

Файл уже создан в `api/.env` со значениями по умолчанию.

Измените при необходимости:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Security
SECRET_KEY=your-super-secret-key

# Marzban (если используется)
MARZBAN_API_URL=http://localhost:8080
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=admin
```

---

## 🎨 Что дальше?

### Кастомизация

1. **Изменить цвета**: `webapp/tailwind.config.ts`
2. **Добавить платформу**: `webapp/src/lib/constants.ts`
3. **Изменить анимации**: `webapp/src/components/*.tsx`

### Деплой

См. полное руководство: [DEPLOYMENT.md](./DEPLOYMENT.md)

Быстрые варианты:
- Vercel (Frontend) + Railway (Backend) - 5 минут
- Docker Compose - 10 минут
- VPS - 30 минут

### Документация

- 📖 [WEBAPP_GUIDE.md](./WEBAPP_GUIDE.md) - Полное руководство
- 📘 [webapp/README.md](./webapp/README.md) - Frontend
- 📗 [api/README.md](./api/README.md) - Backend
- 🚀 [DEPLOYMENT.md](./DEPLOYMENT.md) - Деплой

---

## 🛑 Остановка

### Автоматически

```bash
./stop-webapp.sh
```

### Вручную

```bash
# Найти процессы
ps aux | grep "next-server\|uvicorn"

# Убить процессы
pkill -f "next-server"
pkill -f "uvicorn"

# Или через PM2 (если используется)
pm2 stop webapp
pm2 stop api
```

---

## 🐛 Troubleshooting

### WebApp не запускается

```bash
# Проверьте порт 3000
lsof -i :3000

# Убейте процесс если занят
kill -9 $(lsof -t -i:3000)

# Очистите кэш и переустановите
cd webapp
rm -rf node_modules .next
npm install
npm run dev
```

### API не запускается

```bash
# Проверьте порт 8000
lsof -i :8000

# Убейте процесс если занят
kill -9 $(lsof -t -i:8000)

# Пересоздайте виртуальное окружение
cd api
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

### Ошибки установки зависимостей

#### Frontend

```bash
# Очистите npm кэш
npm cache clean --force

# Удалите package-lock.json
rm package-lock.json

# Переустановите
npm install
```

#### Backend

```bash
# Обновите pip
pip install --upgrade pip

# Установите зависимости заново
pip install -r requirements.txt --no-cache-dir
```

---

## 💡 Полезные команды

### Логи

```bash
# Frontend логи
tail -f webapp.log

# Backend логи
tail -f api.log

# Или в реальном времени через PM2
pm2 logs
```

### Перезапуск

```bash
# Перезапуск всего
./stop-webapp.sh && ./start-webapp.sh

# Только Frontend
pm2 restart webapp

# Только Backend
pm2 restart api
```

### Проверка статуса

```bash
# PM2
pm2 status

# Вручную
curl http://localhost:3000
curl http://localhost:8000/api/health
```

---

## 📞 Помощь

Если что-то не работает:

1. **Проверьте требования** - Node.js 18+, Python 3.11+
2. **Проверьте порты** - 3000 и 8000 должны быть свободны
3. **Проверьте логи** - `tail -f webapp.log api.log`
4. **Создайте Issue** - [GitHub Issues](https://github.com/yourusername/yovpn/issues)

---

## ✅ Чеклист запуска

- [ ] Node.js 18+ установлен
- [ ] Python 3.11+ установлен
- [ ] Зависимости установлены (`npm install`, `pip install`)
- [ ] .env файлы настроены
- [ ] Frontend запущен (http://localhost:3000)
- [ ] Backend запущен (http://localhost:8000)
- [ ] Dev Mode работает (кнопка 🛠️ видна)
- [ ] API Health check отвечает
- [ ] WebApp handler добавлен в бота
- [ ] Команда /webapp работает в боте

---

<p align="center">
  <b>🎉 Поздравляем! YoVPN WebApp готов к использованию!</b><br>
  <sub>Следующий шаг: <a href="./DEPLOYMENT.md">Деплой в production</a></sub>
</p>
